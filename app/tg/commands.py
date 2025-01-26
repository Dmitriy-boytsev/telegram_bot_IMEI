from sqlalchemy.future import select
from telegram import Update
from telegram.ext import CallbackContext

from app.core.db.database_utils import (
    add_user_to_whitelist,
    get_user_by_telegram_id,
    remove_user_from_whitelist,
)
from app.core.db.session import async_session
from app.fastapi.endpoints import assign_admin
from app.fastapi.models import Admin, User


async def check_admin(update: Update, db):
    """Проверка, является ли пользователь администратором."""
    user_id = update.effective_user.id
    admin = await get_user_by_telegram_id(db, user_id)
    return admin and admin.is_admin


async def start(update: Update, context):
    """Приветствие и проверка доступа пользователя."""
    user_id = update.effective_user.id
    async with async_session() as db:
        user = await get_user_by_telegram_id(db, user_id)
        if not user or not user.is_whitelisted:
            await update.message.reply_text("Доступ запрещён. Вы не в белом списке.")
            return
    await update.message.reply_text("Добро пожаловать! Отправьте IMEI для проверки.")


async def list_admins_command(update: Update, context: CallbackContext):
    """Вывод списка администраторов."""
    async with async_session() as db:
        if not await check_admin(update, db):
            await update.message.reply_text("Вы не администратор!")
            return

        result = await db.execute(select(Admin))
        admins = result.scalars().all()

        if not admins:
            await update.message.reply_text("Список администраторов пуст.")
            return

        response = "\n".join([f"{admin.telegram_id} ({admin.username or 'Не указано'})" for admin in admins])
        await update.message.reply_text(f"Администраторы:\n{response}")


async def list_whitelist_command(update: Update, context: CallbackContext):
    """Вывод белого списка пользователей."""
    async with async_session() as db:
        if not await check_admin(update, db):
            await update.message.reply_text("Вы не администратор!")
            return

        result = await db.execute(select(User).filter(User.is_whitelisted == True))
        whitelist = result.scalars().all()

        if not whitelist:
            await update.message.reply_text("Белый список пуст.")
            return

        response = "\n".join([f"{user.telegram_id} ({user.username or 'Не указано'})" for user in whitelist])
        await update.message.reply_text(f"Белый список:\n{response}")


async def add_to_whitelist_command(update: Update, context: CallbackContext):
    """Добавление пользователя в белый список."""
    async with async_session() as db:
        if not await check_admin(update, db):
            await update.message.reply_text("Вы не администратор!")
            return

        if len(context.args) < 1:
            await update.message.reply_text("Используйте команду: /add_to_whitelist <telegram_id> [username]")
            return

        target_id = int(context.args[0])
        target_username = context.args[1] if len(context.args) > 1 else None
        await add_user_to_whitelist(db, target_id, target_username)
        await update.message.reply_text(f"Пользователь {target_id} добавлен в белый список.")


async def remove_from_whitelist_command(update: Update, context: CallbackContext):
    """Удаление пользователя из белого списка."""
    async with async_session() as db:
        if not await check_admin(update, db):
            await update.message.reply_text("Вы не администратор!")
            return

        if len(context.args) < 1:
            await update.message.reply_text("Используйте команду: /remove_from_whitelist <telegram_id>")
            return

        target_id = int(context.args[0])
        await remove_user_from_whitelist(db, target_id)
        await update.message.reply_text(f"Пользователь {target_id} удалён из белого списка.")


async def make_admin_command(update: Update, context: CallbackContext):
    """Назначение пользователя администратором."""
    async with async_session() as db:
        if not await check_admin(update, db):
            await update.message.reply_text("Вы не администратор!")
            return

        if len(context.args) < 1:
            await update.message.reply_text("Используйте команду: /make_admin <telegram_id>")
            return

        target_id = int(context.args[0])
        admin = await assign_admin(db, target_id)
        if admin:
            await update.message.reply_text(f"Пользователь {target_id} назначен администратором.")
        else:
            await update.message.reply_text("Ошибка при назначении администратора.")
