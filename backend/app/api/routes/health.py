from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import HealthResponse
from app.db.base import get_db
from app.core.logger import logger
import aiohttp

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)):
    status = "healthy"
    db_ok = False
    redis_ok = False
    bot_api_ok = False

    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status = "unhealthy"

    try:
        from app.core.config import settings
        import redis.asyncio as redis

        redis_client = redis.from_url(settings.REDIS_URL)
        await redis_client.ping()
        redis_ok = True
        await redis_client.close()
    except Exception as e:
        logger.warning(f"Redis health check failed (optional): {e}")
        redis_ok = False

    try:
        from app.core.config import settings
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{settings.BOT_API_URL}/bot{settings.BOT_TOKEN}/getMe", timeout=5) as response:
                if response.status == 200:
                    bot_api_ok = True
    except Exception as e:
        logger.error(f"Bot API health check failed: {e}")
        status = "unhealthy"

    return HealthResponse(
        status=status,
        database=db_ok,
        redis=redis_ok,
        bot_api=bot_api_ok
    )
