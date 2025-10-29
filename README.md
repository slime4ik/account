# Система аутентификации и авторизации с JWT

### Содержание
- [Локальная разработка](#локальная-разработка)
- [Эндпоинты](#api-endpoints)
- [Разграничение прав доступа](#разграничение-прав-доступа)
- [Запуск тестов](#запуск-тестов-с-coverage95-покрытие-кода)
- [Продакшен](#продакшен)
---

### Локальная разработка
> (должна быть поднята база с именем account, можно использовать sqlite)
```bash
# 1. Клонируй репозиторий
git clone https://github.com/slime4ik/account.git
cd account

# 2. Создай и активируй env
python3 -m venv env
source env/bin/activate  # Для Windows: env\Scripts\activate

# 3. Примени миграции
python manage.py migrate

# 4. Создай суперпользователя
python manage.py createsuperuser

# 5. После создания 2 пользователей можно создать дневники для них
python mange.py create_initial_data
```
## API Endpoints
### DEBUG URLS(основные)
- `GET /api/schema/swagger-ui/` — Свагер(все готово просто подставь свои данные)
- `GET /silk/` — silk Для просмотра количества запросов в БД
- `POST /api/token/` — Получение токенов по username и password

### Аутентификация и Авторизация
- `DELETE /api/users/delete/` — soft delete и токены в блэклист
- `POST /api/users/login/` — Вход
- `POST /api/users/register/` — Регистрация
- `POST /api/users/logout/` — Выход с добавлением токена в блэклист
- `PATCH /api/users/update/` — Обновление профиля(как полностью так и частично)
- `POST /api/token/refresh/` — Обновление access токена
### Разграничение прав доступа.
- `GET /api/dairy/<int:dairy_id>` — Получение дневника по id(если дневник чужой-403, не залогинен-401, создатель-200)

### Запуск тестов с coverage(95% покрытие кода)
```bash
# Запуск тестов
coverage run manage.py test
# Посмотреть покрытие кода в %
coverage report -m
```

### Продакшен
nginx, свои домены, cors и т.д сам напишешь
```bash
# 1. В supermaster/settings/__init__.py измени:
# from .local import *  # для разработки
from .prod import *  # для продакшена
# 2. Создай .env и вставь содержимое из .env.prod.example
# 3. Запусти контейнер
docker-compose up -d --build
```
