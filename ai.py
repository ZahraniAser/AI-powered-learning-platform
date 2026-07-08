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
        f"You are a programming teacher. Create a short beginner lesson about "
        f"'{topic}' (under 200 words). Then give ONE small coding exercise about it.\n\n"
        f"Format your reply exactly like this:\n"
        f"LESSON:\n"
        f"<the lesson here>\n"
        f"EXERCISE:\n"
        f"<the exercise here>"
    )
    response = model.generate_content(prompt)
    text = response.text

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