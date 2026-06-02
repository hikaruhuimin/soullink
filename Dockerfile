FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libssl-dev ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data soullink/static/images

EXPOSE 8080

CMD ["sh", "-c", "echo '=== ENV CHECK ===' && env | grep -iE 'POSTGRES|DATABASE|PORT' | sed 's/PASSWORD=.*/PASSWORD=***/' && echo '=== STARTING ===' && gunicorn --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 120 --access-logfile - --error-logfile - app:app"]
