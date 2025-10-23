FROM python:3.11-slim

WORKDIR /app

# Установка curl для health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

# Добавляем текущую директорию в PYTHONPATH
ENV PYTHONPATH=/app

EXPOSE 8000

# Команда для запуска приложения с миграциями
CMD alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000
