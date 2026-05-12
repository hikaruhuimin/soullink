FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p data soullink/static/images

EXPOSE 8080

CMD ["gunicorn", "wsgi:app", "--bind", "0.0.0.0:8080", "--workers", "1", "--threads", "2", "--timeout", "60"]
# Rebuild 2026年 5月 11日 21:20 JST - force fresh deploy with new templates
