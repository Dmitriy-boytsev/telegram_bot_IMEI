import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.config import settings
from app.core.db.database_utils import (
    add_user_to_whitelist,
    get_user_by_telegram_id,
    remove_user_from_whitelist,
)
from app.core.db.session import get_db
from app.fastapi.models import Admin, User
from app.fastapi.shemas import IMEICheckRequest, IMEICheckResponse, UserWhitelistRequest
from app.fastapi.utils import check_imei_with_api, validate_and_normalize_imei

logging.basicConfig(level=logging.INFO)


api_key_header = APIKeyHeader(name="Authorization", auto_error=True)

router = APIRouter()

@router.get("/whitelist/list")
async def get_whitelist(db: AsyncSession = Depends(get_db)):
    """
    Получение списка пользователей в белом списке.
    """
    result = await db.execute(select(User).filter(User.is_whitelisted == True))
    whitelist = result.scalars().all()
    return {"whitelist": [{"telegram_id": user.telegram_id, "username": user.username} for user in whitelist]}


@router.get("/admin/list")
async def get_admins(db: AsyncSession = Depends(get_db)):
    """
    Получение списка администраторов.
    """
    result = await db.execute(select(Admin))
    admins = result.scalars().all()
    return {"admins": [{"telegram_id": admin.telegram_id, "username": admin.username} for admin in admins]}


@router.post("/whitelist/add")
async def add_to_whitelist(request: UserWhitelistRequest, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для добавления пользователя в белый список.
    """
    user = await add_user_to_whitelist(db, request.telegram_id, request.username)
    return {"message": f"User {request.telegram_id} added to whitelist", "user": user}


@router.post("/whitelist/remove")
async def remove_from_whitelist(request: UserWhitelistRequest, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для удаления пользователя из белого списка.
    """
    user = await remove_user_from_whitelist(db, request.telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found or not in whitelist")
    return {"message": f"User {request.telegram_id} removed from whitelist"}


@router.get("/whitelist/check/{telegram_id}")
async def check_whitelist(telegram_id: int, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для проверки, находится ли пользователь в белом списке.
    """
    user = await get_user_by_telegram_id(db, telegram_id)
    if not user or not user.is_whitelisted:
        return {"telegram_id": telegram_id, "in_whitelist": False}
    return {"telegram_id": telegram_id, "in_whitelist": True, "username": user.username}


async def assign_admin(db: AsyncSession, telegram_id: int, username: Optional[str] = None):
    """Назначение пользователя администратором."""
    admin = await db.execute(select(Admin).filter(Admin.telegram_id == telegram_id))
    existing_admin = admin.scalars().first()
    
    if existing_admin:
        return existing_admin

    user_result = await db.execute(select(User).filter(User.telegram_id == telegram_id))
    user = user_result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_admin = Admin(telegram_id=telegram_id, username=username or user.username)
    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    return new_admin


@router.post("/admin/make_admin")
async def make_admin(request: UserWhitelistRequest, db: AsyncSession = Depends(get_db)):
    """
    Эндпоинт для назначения администратора.
    """
    try:
        admin = await assign_admin(db, request.telegram_id, request.username)
        return {"message": f"User {request.telegram_id} is now an admin", "admin": {"telegram_id": admin.telegram_id, "username": admin.username}}
    except HTTPException as e:
        logging.error(f"Failed to assign admin: {str(e)}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/api/check-imei", response_model=IMEICheckResponse)
async def check_imei(request: IMEICheckRequest, token: str = Depends(api_key_header)):
    """Проверка IMEI через внешний API."""
    logging.info(f"Received token: {token}")

    if not (token == settings.API_TOKEN or token == f"Bearer {settings.API_TOKEN}"):
        logging.error(f"Invalid token: {token}")
        raise HTTPException(status_code=403, detail="Invalid token")

    normalized_imei = validate_and_normalize_imei(request.imei)
    if not normalized_imei:
        logging.error(f"Invalid IMEI: {request.imei}")
        raise HTTPException(status_code=400, detail="Invalid IMEI")

    try:
        data = await check_imei_with_api(normalized_imei, request.serviceid)
        logging.info(f"IMEI check successful for IMEI: {normalized_imei}")
        return IMEICheckResponse(details=data.get("properties", {}))
    except Exception as e:
        logging.error(f"External API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"IMEI API error: {str(e)}")
