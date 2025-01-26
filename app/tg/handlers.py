import requests
from telegram import Update

from app.core.config import settings
from app.core.db.database_utils import get_user_by_telegram_id
from app.core.db.session import async_session


async def handle_message(update: Update, context):
    """Обработка сообщения и проверка IMEI."""
    async with async_session() as db:
        user_id = update.effective_user.id
        user = await get_user_by_telegram_id(db, user_id)

        if not user or not user.is_whitelisted:
            await update.message.reply_text("Доступ запрещён. Вы не в белом списке.")
            return

    imei = update.message.text
    max_retries = 3

    for attempt in range(max_retries):
        try:
            response = requests.post(
                settings.LOCAL_API_URL,
                headers={"Authorization": f"Bearer {settings.API_TOKEN}", "Content-Type": "application/json"},
                json={"imei": imei, "serviceid": 15},
            )

            if response.status_code in {200, 201}:
                data = response.json().get("details", {})
                if not data:
                    await update.message.reply_text("Информация об IMEI не найдена.")
                    return

                result = "<b>Информация об устройстве:</b>\n"
                for key, value in data.items():
                    if isinstance(value, bool):
                        value = "Да" if value else "Нет"
                    result += f"🔹 <b>{key}:</b> {value}\n"

                await update.message.reply_text(result, parse_mode="HTML")
                return
            else:
                if attempt == max_retries - 1:
                    await update.message.reply_text(
                        f"Ошибка: {response.status_code} -- {response.text}. Не удалось выполнить запрос."
                    )
                    return
        except Exception as e:
            if attempt == max_retries - 1:
                await update.message.reply_text(f"Ошибка: {str(e)}. Не удалось выполнить запрос.")
                return
