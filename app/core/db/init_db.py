from app.core.db.session import engine
from app.fastapi.models import Base


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)