FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1
ENV DEBUG false

RUN mkdir /app
WORKDIR /app

COPY pyproject.toml poetry.lock /app/

RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers postgresql-dev

RUN pip install --no-cache-dir poetry virtualenv \
    && poetry config virtualenvs.create false \
    && poetry install --no-interaction --only main \
    && pip install setuptools

RUN apk del .tmp-build-deps

COPY . /app

RUN adduser -D runner
USER runner
