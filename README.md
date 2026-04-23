# Quiz App

A 40-question quiz covering Maths, Java, Python & Statistics.

## Local Run
```bash
python server.py
# Open http://localhost:8080
```

## Deploy on Railway
1. Push this folder to a GitHub repo
2. Go to https://railway.app → New Project → Deploy from GitHub
3. Select the repo — Railway auto-detects Python and uses the Procfile
4. Your app will be live at the Railway-provided URL

## Scores
- Saved to `scores.csv` on the server
- View all scores at `/scores` endpoint
