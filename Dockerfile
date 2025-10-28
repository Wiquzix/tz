FROM python:3.11

WORKDIR /app

RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

ENV POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_NO_INTERACTION=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root --only main

COPY . .

EXPOSE 8000

CMD poetry run alembic upgrade head && poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
