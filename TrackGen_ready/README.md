# TrackGen — Ready-to-deploy Flask MVP (clean folder)

This package is a ready-to-run minimal Flask app for the TrackGen AI Visibility dashboard prototype.
It is intentionally simple and includes a Dockerfile so Render/Railway/Heroku can run it directly.

## Quick local run
  python -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  python app.py
  Open http://127.0.0.1:5000

## Quick Docker
  docker build -t trackgen:latest .
  docker run -p 5000:5000 --env FLASK_SECRET=change_me trackgen:latest

## Deploy on Render
1. Push this repo to GitHub.
2. In Render create a new Web Service -> Connect repo.
3. Use Docker environment (Render will use Dockerfile).
4. Add environment vars in Render dashboard.
5. Deploy.

## Env vars (optional)
  FLASK_SECRET - required
  PERPLEXITY_API_KEY - optional for Perplexity calls
  GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET - optional for OAuth (not enabled by default)
  SENDGRID_API_KEY - optional for email sending
  REDIS_URL - optional for RQ worker

Replace static/sample_ad.mp4 with a real ad or integrate Google Ad Manager later.
