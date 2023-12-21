# Используем образ Python
FROM python:3.9

# Устанавливаем рабочую директорию в /app
WORKDIR /app

# Копируем requirements.txt в текущую директорию образа
COPY requirements.txt .

# Устанавливаем зависимости из requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы из текущей директории (где находится Dockerfile) в /app в образе
COPY . .

# Выполняем миграции
RUN python manage.py makemigrations && python manage.py migrate

# Создаем администатора
RUN echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@myproject.com', 'password')" | python manage.py shell

# Заполняем базу данных с использованием фикстур
RUN python manage.py loaddata tree/fixtures/menu.json
RUN python manage.py loaddata tree/fixtures/menuitem.json

# Указываем, что приложение будет доступно на порту 8000
EXPOSE 8000

# Запускаем приложение
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
