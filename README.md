
# Telegram IMEI Checker Bot

Проект представляет собой Telegram-бот, предназначенный для управления пользователями и проверки IMEI через внешние API. Бот включает функции управления администраторами и белым списком, а также проверки IMEI.

## Функционал

- **Управление пользователями:**
  - Добавление или удаление пользователей из белого списка.
  - Проверка, находится ли пользователь в белом списке.
  - Назначение или снятие ролей администратора.

- **Управление IMEI:**
  - Проверка IMEI на корректность.
  - Запрос деталей IMEI из внешнего API.
  - Отображение результатов пользователям.

- **Команды бота:**
  - `/start` - Начало работы и проверка доступа пользователя.
  - `/add_to_whitelist <telegram_id> [username]` - Добавляет пользователя в белый список.
  - `/remove_from_whitelist <telegram_id>` - Удаляет пользователя из белого списка.
  - `/make_admin <telegram_id>` - Назначает пользователя администратором.
  - `/list_admins` - Отображает список администраторов.
  - `/list_whitelist` - Отображает список пользователей в белом списке.

## Структура проекта

```plaintext
app/
├── core/
│   ├── config.py              # Конфигурация бота
│   └── db/                    # Утилиты для работы с базой данных
├── fastapi/
│   ├── endpoints.py           # Эндпоинты FastAPI
│   ├── models.py              # SQLAlchemy модели базы данных
│   ├── schemas.py             # Pydantic схемы для валидации данных
│   └── utils.py               # Утилиты для проверки IMEI и взаимодействия с API
├── tg/
│   ├── commands.py            # Обработчики команд для Telegram бота
│   ├── handlers.py            # Обработчики сообщений для Telegram бота
│   ├── router.py              # Регистрация обработчиков Telegram бота
│   └── utils.py               # Утилиты, специфичные для Telegram
├── main.py                    # Точка входа для запуска бота
```

## Установка и настройка

### Требования
- Python 3.9+
- PostgreSQL (или любая предпочитаемая база данных)
- Telegram Bot Token
- IMEI API Token

### Шаги
1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-repo/telegram-imei-bot.git
   cd telegram-imei-bot
   ```

2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

3. Настройте переменные окружения в `.env`:
   ```plaintext
   TOKEN_API_SANDBOX = "**********SANDBOX_TOKEN**********"
   TOKEN_API_LIVE = "**********LIVE_TOKEN**********"
   TELEGRAM_BOT_TOKEN = "**********BOT_TOKEN**********"

   DATABASE_URL = "postgresql+asyncpg://user:password@localhost/database"
   POSTGRES_USER = "your_postgres_user"
   POSTGRES_PASSWORD = "your_postgres_password"
   POSTGRES_DB = "your_database_name"

   API_TOKEN = "**********API_TOKEN**********"
   LOCAL_API_URL = "http://127.0.0.1:8000/api/check-imei"

   APP_TITLE = "Checker IMEI API"
   DESCRIPTION = "API для проверки IMEI"
   VERSION = "1.0.0"
   ```

4. Инициализируйте базу данных:
   ```bash
   alembic upgrade head
   ```

5. Запустите бота:
   ```bash
   python main.py
   ```

## Использование

- Взаимодействуйте с ботом через Telegram, используя команды.
- Используйте эндпоинты FastAPI для дополнительных операций:
  - `POST /api/check-imei`
  - `GET /whitelist/list`
  - `POST /whitelist/add`
  - И другие.

