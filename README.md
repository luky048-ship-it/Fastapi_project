### Ментору: да я вкурсе что надобыло делать один и вы его показывали на занятии, решил оба варианта и чуть-чуть более сложним путем, просто в качестве обучения.
# FastAPI Microservices Project: TODO List & URL Shortener
Данный репозиторий содержит два независимых микросервиса, разработанных на Python (FastAPI) с использованием базы данных SQLite для постоянного хранения данных (Persistent Storage). 
Оба сервиса полностью контейнеризированы с помощью Docker.
## Сводная информация о проекте

| Сервис | Технологии | Порт (Хост) | Хранилище (Docker Volume) |
| :--- | :--- | :--- | :--- |
| **TODO Service** | FastAPI, SQLite | `8000` | `todo_data` |
| **URL Shortener** | FastAPI, SQLite | `8001` | `shorturl_data` |

## Запуск контейнеров

Запуск готовых образов осуществляется одной командой, которая автоматически скачивает их с Docker Hub и монтирует тома для сохранения данных.

```bash
# 1. Запуск TODO Service: маппинг порта 8000 на порт 80 контейнера.
docker run -d --name todo_app -p 8000:80 -v todo_data:/app/data stassl048/todo-service:latest

# 2. Запуск Shortener Service: маппинг порта 8001 на порт 80 контейнера.
docker run -d --name shorturl_app -p 8001:80 -v shorturl_data:/app/data stassl048/shorturl:latest
```


## Справочник команд Docker (Шпаргалка)

| Команда | Назначение | Примечание |
| :--- | :--- | :--- |
| `docker build -t name:tag ./folder` | Сборка нового образа из `Dockerfile`. | `-t` (tag) задает имя и версию. |
| `docker run -d -p ХХХХ:80 -v vol:/path image` | Запуск контейнера в фоновом режиме. | `-p X:Y` (проброс порта), `-v name:path` (монтирование тома). |
| `docker ps` | Проверка статуса запущенных контейнеров. | Показывает ID, имена, порты и статус (`Up/Exited`). |
| `docker stop <name or id>` | Корректно остановить работающий контейнер. | Использовать `docker rm -f` для немедленного удаления. |
| `docker push name:tag` | Отправить локальный образ в облако Docker Hub. | Требует предварительного `docker login`. |
| `docker volume ls` | Посмотреть список всех созданных именованных томов. | Необходимо для управления данными (удаления/проверки). |

## Типовая проверка и диагностика контейнеров

| Команда | Назначение | Ожидаемый результат |
| :--- | :--- | :--- |
| `docker ps --filter "name=todo_app"` | Проверка, запущен ли контейнер. | Статус должен быть **`Up ...`** (работает). |
| `curl http://localhost:8000/docs` | Проверка доступности API (HTTP). | Возвращает код `200` и HTML-код страницы Swagger. |
| `docker logs todo_app` | Просмотр логов контейнера. | Показывает сообщения сервера FastAPI (например, `Uvicorn running on http://0.0.0.0:80`). |
| `docker exec -it todo_app ls /app/data` | Проверка наличия базы данных внутри тома. | Должен показать файл базы данных (`todo.db`). |


### 3. Тестирование API (cURL Examples)

Примеры команд для быстрой проверки функциональности сервисов через терминал.

#### A. Проверка TODO Service (Порт 8000)

```bash
# 1. Создание новой задачи (POST)
curl -X 'POST' 'http://localhost:8000/items' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "title": "Срочный проект",
  "description": "Проверить работу Volumes"
}'

# 2. Получение всех задач (GET)
curl -X 'GET' 'http://localhost:8000/items' -H 'accept: application/json'
```
#### B. Проверка URL Shortener Service (Порт 8001)

```bash
# 1. Сокращение длинного URL (POST)
curl -X 'POST' 'http://localhost:8001/shorten' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "url": "[https://docs.docker.com/get-started/overview/](https://docs.docker.com/get-started/overview/)"
}'

# 2. Перенаправление по короткому коду (GET)
# NOTE: Замените 'XyZ123' на код, полученный в ответе на POST-запрос.
curl -I -L 'http://localhost:8001/XyZ123'
```
