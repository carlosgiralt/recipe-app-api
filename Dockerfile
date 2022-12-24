FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1
ENV DEBUG false

RUN mkdir /app
WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN pip install --no-cache-dir poetry virtualenv \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --only main \
    && pip install setuptools

COPY . /app

RUN adduser -D runner
USER runner
