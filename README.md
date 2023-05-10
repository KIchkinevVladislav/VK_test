REST API для сервиса ***VK_test_friends**. 
База статусов дружбы между пользователями.

**Описание**
Проект **VK_test_friends** позволяет пользователя создавать дружбу в сети.

В **VK_test_friends** реализованы следующие возможности:
    - регистрация пользователя
    - отправка заявки на добавление в друзья
    - прием/отклонение заявок
    - получать пользователю статус дружбы с другим пользователей или наличие заявок
    - удалить пользователя из друзей
    - автоматическое добавление в друзья при наличии встречных заявок



[Спецификация OpenAPI (redoc_vk_test.yaml)](https://github.com/KIchkinevVladislav/VK_test/blob/main/static/redoc_vk_test.yaml)

[Краткое руководство пользователя по запуску и использованию  (VK_test_friends_short_documentation.pdf)](https://github.com/KIchkinevVladislav/VK_test/blob/main/static/redoc_vk_test.yaml)


#### Стек технологий:
- Python3.10
- Django - база данных
- Django REST framework - REST API
- drf-spectacular - documentation

#### Запуск приложения.

Установите зависимости из requirements.txt:

`pip install -r requirements.txt`

Выполните все необходимые миграции:

`python manage.py makemigrations`

`python manage.py migrate`

Для доступа к панели администратора создайте администратора:

`python manage.py createsuperuser`

Запустите приложение:

`python manage.py runserver`