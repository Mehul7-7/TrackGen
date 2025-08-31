FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends         curl ca-certificates build-essential libnss3 libatk1.0-0 libasound2 libx11-xcb1 libxcomposite1 libxrandr2 libgtk-3-0 libgbm-dev wget         && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

RUN playwright install chromium

COPY . /app
ENV PORT=5000
EXPOSE 5000
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000", "--workers", "2"]
