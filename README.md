# AI Coding Tutor

A small web app that teaches a programming topic, gives an exercise, and checks
your answer using AI.

Built with FastAPI, PostgreSQL (Neon), and the Google Gemini API.

## How it works

1. You type a topic (e.g. "loops in Python").
2. The AI writes a short lesson and one exercise.
3. You write your answer and submit it.
4. The AI checks it and gives feedback.

Lessons and submissions are saved in the database.

## Setup

### 1. Install dependencies

```
pip install -r requirements.txt
```

(Optional but recommended: make a virtual environment first with
`python -m venv venv` and activate it.)

### 2. Get a free Neon database

- Go to https://neon.tech and sign up (no credit card needed).
- Create a project. It gives you a connection string.
- Copy that connection string.

### 3. Get a free Gemini API key

- Go to https://aistudio.google.com/apikey
- Create an API key and copy it.

### 4. Add your keys

- Copy `.env.example` to `.env`.
- Paste your Neon connection string into `DATABASE_URL`.
- Paste your Gemini key into `GEMINI_API_KEY`.

### 5. Run it

```
uvicorn main:app --reload
```

Then open http://127.0.0.1:8000 in your browser.

## Files

- `main.py` - the FastAPI app and routes
- `database.py` - database connection setup
- `models.py` - the database tables
- `ai.py` - the Gemini calls (generate lesson, check answer)
- `static/index.html` - the frontend page

## Deploying online

The whole thing is one app, so you can deploy it to a free host like Render:

- Push this folder to GitHub.
- On Render, create a new Web Service from the repo.
- Set the start command to: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add `DATABASE_URL` and `GEMINI_API_KEY` as environment variables.
