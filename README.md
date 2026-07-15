# AI Coding Tutor

A web app that teaches programming topics, gives exercises, and checks your
answers using AI. It saves your progress and history.

Built with Streamlit, PostgreSQL (Neon), and the Google Gemini API.

## Features

- Enter your name to start - your progress is saved under it
- The AI writes a short lesson and one exercise for any programming topic
- The AI checks your answer, gives pass/fail and an explanation
- Only teaches programming (other topics are politely turned away)
- Tracks how many exercises you attempted and passed, and which topics
- Suggests what to learn next based on what you've already done
- Full history you can expand to see the lesson, exercise, your answer and feedback

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

### 3. Get a free Gemini API key

- Go to https://aistudio.google.com/apikey and create a key.

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

- `app.py` - the Streamlit app (the interface and the glue)
- `database.py` - database connection setup
- `models.py` - the database tables (users, lessons, submissions)
- `ai.py` - the Gemini calls (generate lesson, check answer, suggest topics)
- `.streamlit/config.toml` - the dark theme settings

## Deploying online (free)

Hosted for free on Streamlit Community Cloud:

1. Push this folder to a GitHub repository.
   (Make sure `.env` is NOT pushed - the included `.gitignore` handles this.)
2. Go to https://share.streamlit.io and sign in with GitHub.
   For a private repo, grant Streamlit access to private repositories.
3. Click "New app" and pick your repository. Set the main file to `app.py`.
4. In "Advanced settings" -> "Secrets", add your two keys in TOML format:
   ```
   DATABASE_URL = "your neon string"
   GEMINI_API_KEY = "your gemini key"
   ```
5. Deploy. You get a public link you can share.

After the first deploy, pushing to GitHub updates the live app automatically.

## Notes

- The free Gemini tier allows only a few requests per minute, shared across
  everyone using the app. The app shows a friendly message if that limit is hit.
- The free hosting and the free database both sleep when idle, so the first
  visit after a quiet period takes a little longer to load.
