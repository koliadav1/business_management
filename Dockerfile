FROM python:3.13-slim

WORKDIR /app

RUN useradd -m -u 1000 appuser \
    && chown -R appuser:appuser /app

COPY pyproject.toml .

RUN pip install --upgrade pip \
    && pip install .

COPY . .

USER appuser