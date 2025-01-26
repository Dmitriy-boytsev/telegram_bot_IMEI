from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.fastapi.models import User

async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int):
    """Получение пользователя по Telegram ID."""
    result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
    return result.scalars().first()

async def add_user_to_whitelist(db: AsyncSession, telegram_id: int, username: str = None):
    """Добавление пользователя в белый список."""
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user:
        user = User(telegram_id=telegram_id, username=username, is_whitelisted=True)
        db.add(user)
        await db.commit()
        await db.refresh(user)
    else:
        user.is_whitelisted = True
        user.username = username or user.username
        await db.commit()
    return {"telegram_id": user.telegram_id, "username": user.username, "is_whitelisted": user.is_whitelisted}

async def remove_user_from_whitelist(db: AsyncSession, telegram_id: int):
    """Удаление пользователя из белого списка."""
    user = await get_user_by_telegram_id(db, telegram_id)
    if user and user.is_whitelisted:
        user.is_whitelisted = False
        await db.commit()
        return user
    return None

