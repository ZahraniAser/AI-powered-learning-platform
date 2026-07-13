import streamlit as st

import ai
import models
from database import engine, SessionLocal

# Create the database tables if they don't exist yet.
models.Base.metadata.create_all(bind=engine)

st.set_page_config(page_title="AI Coding Tutor", page_icon="📘")

st.title("AI Coding Tutor")
st.write("Type a topic you want to learn, and the AI will teach it and give you an exercise.")

# Keep the current lesson in memory between button clicks.
if "lesson" not in st.session_state:
    st.session_state.lesson_id = None
    st.session_state.lesson = None
    st.session_state.exercise = None

topic = st.text_input("Topic", placeholder="e.g. loops in Python")

if st.button("Teach me"):
    if not topic.strip():
        st.warning("Please type a topic first.")
    else:
        with st.spinner("Thinking..."):
            try:
                lesson_text, exercise = ai.generate_lesson(topic)

                # Save the lesson to the database.
                db = SessionLocal()
                lesson = models.Lesson(
                    topic=topic,
                    lesson_text=lesson_text,
                    exercise=exercise,
                )
                db.add(lesson)
                db.commit()
                db.refresh(lesson)
                st.session_state.lesson_id = lesson.id
                db.close()

                st.session_state.lesson = lesson_text
                st.session_state.exercise = exercise
            except Exception as e:
                st.error(f"Something went wrong: {e}")

# Show the lesson and exercise once we have one.
if st.session_state.lesson:
    st.subheader("Lesson")
    st.markdown(st.session_state.lesson)

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
                    passed, feedback = ai.check_answer(st.session_state.exercise, user_code)

                    # Save the submission.
                    db = SessionLocal()
                    submission = models.Submission(
                        lesson_id=st.session_state.lesson_id,
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
                    st.error(f"Something went wrong: {e}")