import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set. Check your .env file.")

genai.configure(api_key=API_KEY)

# Free-tier model. You can change this to another Gemini model if you want.
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_lesson(topic):
    prompt = (
        f"You are a programming teacher. You ONLY teach programming and software "
        f"development topics (coding languages, programming concepts, tools, computer "
        f"science).\n\n"
        f"The user asked to learn about: '{topic}'\n\n"
        f"If this topic is NOT about programming or software development, reply with "
        f"only this single word and nothing else:\n"
        f"NOT_PROGRAMMING\n\n"
        f"Otherwise, create a short beginner lesson (under 200 words) and ONE small "
        f"coding exercise about it. Format your reply exactly like this:\n"
        f"LESSON:\n"
        f"<the lesson here>\n"
        f"EXERCISE:\n"
        f"<the exercise here>"
    )
    response = model.generate_content(prompt)
    text = response.text.strip()

    # If the topic wasn't about programming, signal that with None.
    if "NOT_PROGRAMMING" in text.upper() and "LESSON:" not in text.upper():
        return None, None

    # Split the reply into the lesson part and the exercise part.
    if "EXERCISE:" in text:
        lesson_part = text.split("EXERCISE:")[0].replace("LESSON:", "").strip()
        exercise_part = text.split("EXERCISE:")[1].strip()
    else:
        lesson_part = text.strip()
        exercise_part = "Try writing a small program about this topic."

    return lesson_part, exercise_part


def check_answer(exercise, user_code):
    prompt = (
        f"You are a programming teacher checking a student's answer.\n"
        f"Exercise: {exercise}\n"
        f"Student's code:\n{user_code}\n\n"
        f"Decide if the code correctly solves the exercise. Explain simply what is "
        f"right or wrong, and if it's wrong show a correct solution.\n\n"
        f"Start your reply with the word PASS or FAIL on its own line, "
        f"then write your feedback after it."
    )
    response = model.generate_content(prompt)
    text = response.text.strip()

    # The first line tells us pass or fail, the rest is the feedback.
    first_line = text.split("\n")[0].upper()
    passed = "PASS" in first_line
    feedback = text.split("\n", 1)[1].strip() if "\n" in text else text

    return passed, feedback


def suggest_next_topics(done_topics):
    done_text = ", ".join(done_topics) if done_topics else "nothing yet"
    prompt = (
        f"You are a programming teacher guiding a student along a C# learning path, "
        f"from beginner to more advanced.\n"
        f"The student has already practiced these topics: {done_text}.\n"
        f"Suggest the next 4 topics they should learn, in a sensible order along the "
        f"path, and avoid topics they have already done.\n"
        f"Reply with only the 4 topics, each on its own line. No numbering, no extra text."
    )
    response = model.generate_content(prompt)
    text = response.text.strip()

    # Turn the reply into a clean list, removing any bullets or numbers.
    topics = []
    for line in text.split("\n"):
        line = line.strip("-*0123456789. ").strip()
        if line:
            topics.append(line)
    return topics[:4]