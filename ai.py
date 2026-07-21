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
        f"Otherwise, write a detailed but beginner-friendly lesson that TEACHES before "
        f"it tests. Give these four parts, using EXACTLY these labels on their own lines:\n\n"
        f"LESSON:\n"
        f"A clear explanation of the concept in simple words, followed by two or three "
        f"worked examples. Each example must show real code and a short explanation of "
        f"what the code does and why.\n\n"
        f"PRACTICE:\n"
        f"One small guided task for the learner to try themselves. Do NOT include the "
        f"solution here.\n\n"
        f"PRACTICE_SOLUTION:\n"
        f"The full solution to the practice task, with code and a short explanation.\n\n"
        f"EXERCISE:\n"
        f"One separate exercise for the learner to solve on their own. Do NOT include "
        f"its solution.\n\n"
        f"Write in Markdown. Put every piece of code inside triple-backtick code blocks."
    )
    response = model.generate_content(prompt)
    text = response.text.strip()

    # If the topic wasn't about programming, signal that with None.
    if "NOT_PROGRAMMING" in text.upper() and "LESSON:" not in text.upper():
        return None, None, None, None

    # Defaults in case a part is missing.
    practice_task = ""
    practice_solution = ""
    exercise_part = "Try writing a small program about this topic."

    # Split off each part one at a time, from the end backwards.
    if "EXERCISE:" in text:
        text, exercise_part = text.split("EXERCISE:", 1)
        exercise_part = exercise_part.strip()

    if "PRACTICE_SOLUTION:" in text:
        text, practice_solution = text.split("PRACTICE_SOLUTION:", 1)
        practice_solution = practice_solution.strip()

    if "PRACTICE:" in text:
        text, practice_task = text.split("PRACTICE:", 1)
        practice_task = practice_task.strip()

    lesson_part = text.replace("LESSON:", "").strip()

    return lesson_part, practice_task, practice_solution, exercise_part


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


def suggest_next_topics(current_topic, done_topics):
    done_text = ", ".join(done_topics) if done_topics else "nothing yet"

    if current_topic:
        focus = (
            f"The student is currently learning about: '{current_topic}'.\n"
            f"Suggest the next 4 topics that follow on naturally from this, staying in "
            f"the same technology or subject area.\n"
        )
    else:
        focus = "Suggest 4 good beginner C# topics to start with.\n"

    prompt = (
        f"You are a programming teacher planning what a student should learn next.\n"
        f"{focus}"
        f"The student has already practiced: {done_text}. Do not repeat those.\n"
        f"Every topic must name its language or technology, for example "
        f"'Variables and data types in C#' or 'Defining models in Odoo'.\n"
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