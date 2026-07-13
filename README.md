# AI Coding Tutor

A small web app that teaches a programming topic, gives an exercise, and checks
your answer using AI.

Built with Streamlit, PostgreSQL (Neon), and the Google Gemini API.

## How it works

1. You type a topic (e.g. "loops in Python").
2. The AI writes a short lesson and one exercise.
3. You write your answer and submit it.
4. The AI checks it and gives feedback (pass/fail plus an explanation).

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
streamlit run app.py
```

Your browser will open automatically at http://localhost:8501

## Files

- `app.py` - the Streamlit app (the whole interface and logic)
- `database.py` - database connection setup
- `models.py` - the database tables
- `ai.py` - the Gemini calls (generate lesson, check answer)
- `.streamlit/config.toml` - the dark theme settings

## Deploying online (free)

You can host this for free on Streamlit Community Cloud:

1. Push this folder to a GitHub repository.
   (Make sure `.env` is NOT pushed - the included `.gitignore` handles this.)
2. Go to https://share.streamlit.io and sign in with GitHub.
3. Click "New app" and pick your repository. Set the main file to `app.py`.
4. In the app's "Secrets" settings, add your two keys:
   ```
   DATABASE_URL = "your neon string"
   GEMINI_API_KEY = "your gemini key"
   ```
5. Deploy. You get a public link you can share.
