from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from app.core.config import settings
from app.tg.commands import (
    add_to_whitelist_command,
    add_user_to_whitelist,
    check_admin,
    list_admins_command,
    list_whitelist_command,
    make_admin_command,
    remove_from_whitelist_command,
    remove_user_from_whitelist,
    start,
)
from app.tg.handlers import handle_message

app_builder = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

def register_handlers(app_builder):
    """
    Регистрирует все обработчики команд и сообщений для бота.
    """
    app_builder.add_handler(CommandHandler("start", start))
    app_builder.add_handler(CommandHandler("add_to_whitelist", add_to_whitelist_command))
    app_builder.add_handler(CommandHandler("remove_from_whitelist", remove_from_whitelist_command))
    app_builder.add_handler(CommandHandler("make_admin", make_admin_command))
    app_builder.add_handler(CommandHandler("list_admins", list_admins_command))
    app_builder.add_handler(CommandHandler("list_whitelist", list_whitelist_command))
    app_builder.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    return app_builder
