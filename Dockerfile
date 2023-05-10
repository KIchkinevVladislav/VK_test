# Используем образ Python 3.10.9
FROM python:3.10.9-slim

# Устанавливаем зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        python3-dev \
        default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем код приложения
WORKDIR /app
COPY . /app

# Устанавливаем зависимости Python
RUN pip install --no-cache-dir -r requirements.txt

# Создаем миграции и выполняем миграции
RUN python manage.py makemigrations
RUN python manage.py migrate

# Запускаем приложение
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
