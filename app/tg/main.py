from telegram import Bot

from app.core.config import settings
from app.tg.router import app_builder, register_handlers

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)



if __name__ == "__main__":
    print("Bot is polling...")
    app = register_handlers(app_builder)
    app.run_polling()
