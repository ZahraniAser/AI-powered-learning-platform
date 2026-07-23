import streamlit as st

import ai
import models
from database import engine, SessionLocal

# Create the database tables if they don't exist yet.
models.Base.metadata.create_all(bind=engine)

st.set_page_config(page_title="AI Coding Tutor", page_icon="📘")

st.title("AI Coding Tutor")


# Show a friendly message instead of a scary error when the free AI limit is hit.
def show_error(e):
    text = str(e).lower()
    if "429" in text or "quota" in text or "rate" in text:
        st.warning("The free AI limit was reached (only a few requests per minute are "
                   "allowed). Please wait about a minute and try again.")
    else:
        st.error(f"Something went wrong: {e}")


# Generate a lesson for a topic, save it, and remember it. Used by both the
# "Teach me" button and the suggested-topic buttons.
def teach(topic_text):
    level = st.session_state.get("level", "Beginner")
    with st.spinner("Thinking..."):
        try:
            lesson_text, practice_task, practice_solution, exercise = \
                ai.generate_lesson(topic_text, level)

            if lesson_text is None:
                st.warning("Please enter a programming topic — for example: "
                           "loops, functions, arrays, or classes in C#.")
                return

            db = SessionLocal()
            lesson = models.Lesson(
                user_id=st.session_state.user_id,
                topic=topic_text,
                lesson_text=lesson_text,
                exercise=exercise,
            )
            db.add(lesson)
            db.commit()
            db.refresh(lesson)
            st.session_state.lesson_id = lesson.id
            db.close()

            st.session_state.lesson = lesson_text
            st.session_state.practice_task = practice_task
            st.session_state.practice_solution = practice_solution
            st.session_state.exercise = exercise
            st.session_state.topic = topic_text
        except Exception as e:
            show_error(e)


# --- Set up remembered values ---
if "user_id" not in st.session_state:
    st.session_state.user_id = None
    st.session_state.username = None
    st.session_state.lesson_id = None
    st.session_state.lesson = None
    st.session_state.practice_task = None
    st.session_state.practice_solution = None
    st.session_state.exercise = None
    st.session_state.topic = None
    st.session_state.suggestions = []


# --- Step 1: ask for a name before anything else ---
if st.session_state.user_id is None:
    st.write("Enter your name to start learning. Your progress will be saved.")
    name = st.text_input("Your name")
    if st.button("Start"):
        if not name.strip():
            st.warning("Please type your name.")
        else:
            db = SessionLocal()
            user = db.query(models.User).filter(
                models.User.username == name.strip()
            ).first()
            if not user:
                user = models.User(username=name.strip())
                db.add(user)
                db.commit()
                db.refresh(user)
            st.session_state.user_id = user.id
            st.session_state.username = user.username
            db.close()
            st.rerun()
    st.stop()


# --- Logged in from here on ---
st.write(f"Welcome, {st.session_state.username}!")

if st.button("Switch user"):
    st.session_state.user_id = None
    st.session_state.lesson = None
    st.session_state.practice_task = None
    st.session_state.practice_solution = None
    st.session_state.exercise = None
    st.session_state.topic = None
    st.session_state.lesson_id = None
    st.session_state.suggestions = []
    st.rerun()


# --- Load this user's data once (used by progress, suggestions, and history) ---
db = SessionLocal()
subs = db.query(models.Submission).filter(
    models.Submission.user_id == st.session_state.user_id
).order_by(models.Submission.created_at.desc()).all()
lessons = db.query(models.Lesson).filter(
    models.Lesson.user_id == st.session_state.user_id
).all()
db.close()

lesson_by_id = {lesson.id: lesson for lesson in lessons}
done_topics = sorted(set(s.topic for s in subs if s.topic))


# --- Progress summary ---
if subs:
    st.subheader("Your progress")
    total = len(subs)
    passed = sum(1 for s in subs if s.passed)
    st.write(f"Exercises attempted: {total}  |  Passed: {passed}")
    if done_topics:
        st.write("Topics practiced: " + ", ".join(done_topics))


# --- Suggested next topics ---
st.subheader("Suggested for you")
st.write("Pick a difficulty level and get topic ideas for what to learn next.")

level = st.radio(
    "Difficulty level",
    ["Beginner", "Intermediate", "Advanced"],
    horizontal=True,
    key="level",
)

if st.button("Suggest what to learn next"):
    with st.spinner("Thinking..."):
        try:
            # Base suggestions on what the user is currently learning, if anything.
            anchor = st.session_state.topic
            if not anchor and subs:
                anchor = subs[0].topic  # otherwise their most recent topic
            st.session_state.suggestions = ai.suggest_next_topics(
                anchor, done_topics, level
            )
        except Exception as e:
            show_error(e)

if st.session_state.suggestions:
    st.write("Click a topic to start learning it:")
    for i, suggested in enumerate(st.session_state.suggestions):
        if st.button(suggested, key=f"suggestion_{i}"):
            teach(suggested)


# --- Pick your own topic ---
st.subheader("Learn something new")
st.write("Or type a programming topic you want to learn.")
topic = st.text_input("Topic", placeholder="e.g. loops in C#")
if st.button("Teach me"):
    if not topic.strip():
        st.warning("Please type a topic first.")
    else:
        teach(topic)


# --- Show the current lesson and check the answer ---
if st.session_state.lesson:
    st.subheader("Lesson")
    st.markdown(st.session_state.lesson)

    # Practice: a try-it-yourself step. The box is a scratchpad (not graded),
    # and the solution is hidden until the learner clicks to reveal it.
    if st.session_state.practice_task:
        st.subheader("Practice (try it yourself, then reveal the solution)")
        st.markdown(st.session_state.practice_task)
        st.text_area("Your practice attempt (not graded)", height=150,
                     key="practice_box")
        with st.expander("Show solution"):
            st.markdown(st.session_state.practice_solution)

    st.subheader("Exercise")
    st.markdown(st.session_state.exercise)

    st.subheader("Your answer")
    user_code = st.text_area("Write your code here", height=200)

    if st.button("Check my answer"):
        if not user_code.strip():
            st.warning("Please write your answer first.")
        else:
            with st.spinner("Checking..."):
                try:
                    passed, feedback = ai.check_answer(
                        st.session_state.exercise, user_code
                    )

                    db = SessionLocal()
                    submission = models.Submission(
                        user_id=st.session_state.user_id,
                        lesson_id=st.session_state.lesson_id,
                        topic=st.session_state.topic,
                        user_code=user_code,
                        feedback=feedback,
                        passed=passed,
                    )
                    db.add(submission)
                    db.commit()
                    db.close()

                    st.subheader("Feedback")
                    if passed:
                        st.success("Correct!")
                    else:
                        st.error("Not quite yet.")
                    st.markdown(feedback)
                except Exception as e:
                    show_error(e)


# --- History of past attempts ---
st.subheader("My history")
if subs:
    for s in subs:
        result = "Passed" if s.passed else "Not passed"
        date = s.created_at.strftime("%d %b %Y, %H:%M") if s.created_at else ""
        with st.expander(f"{s.topic}  —  {result}  —  {date}"):
            lesson = lesson_by_id.get(s.lesson_id)
            if lesson:
                st.markdown("**The lesson you were given:**")
                st.markdown(lesson.lesson_text)
                st.markdown("**Exercise:**")
                st.markdown(lesson.exercise)
            st.markdown("**Your answer:**")
            st.code(s.user_code)
            st.markdown("**Feedback:**")
            st.markdown(s.feedback)
else:
    st.write("No history yet. Complete an exercise and it will show up here.")