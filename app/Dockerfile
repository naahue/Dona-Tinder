FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app
WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python -c "import config.wsgi; import config.urls"

# Si faltan fixtures o comando seed, falla el build antes de compose.
RUN test -f donacion/management/commands/seed_docker_demo.py \
    && test -f donacion/fixtures/seed_demo/banera.png \
    && test -f donacion/fixtures/seed_demo/cama_ambiente.png \
    && test -f donacion/fixtures/seed_demo/tv_smart.png

RUN DJANGO_DEBUG=true DJANGO_ALLOWED_HOSTS=localhost python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "--pythonpath", "/app", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
