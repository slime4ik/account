FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# # collect static (react, admin, etc.)
# RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "supermaster.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]