FROM python:3.12-slim AS base

WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development

ENV FLASK_ENV=development
ENV FLASK_DEBUG=True
ENV PYTHONUNBUFFERED=1

COPY . .

EXPOSE 3000

ENV FLASK_APP=app.utils.factory:create_app
CMD ["flask", "run", "--host=0.0.0.0", "--port=3000"]
