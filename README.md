# Сервис друзей

## Скачивание проекта
Копируем репозиторий и заходим в директорию:

```
git clone https://github.com/gukkt/vk_internship.git
cd vk_internship
```

## Запуск проекта
1. ### Запуск проекта с докером:
    ```
    docker build -t friends-service .
    docker run friends-service test
    docker run -p 8080:8000 friends-service
    ```

2. ### Запуск проекта без докера:
   1. Создаём переменную окружения:
       ```
       python3.11 -m venv venv
       source venv/bin/activate
       ```
   2. Устанавливаем зависимости:
       ```
       pip install -r requirements.txt
       ```
   3. Накатываем миграции:
       ```
       python manage.py migrate
       ```
   4. Запускаем тесты:
       ```
       python manage.py test
       ```
   5. 
   5Запускаем проект:
       ```
       python manage.py runserver
       ```
