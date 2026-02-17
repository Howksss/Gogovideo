from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.schemas import AuthValidateRequest, AuthResponse, InitResponse, VideoResponse
from app.db.base import get_db
from app.db.crud import UserCRUD, VideoCRUD
from app.core.security import validate_telegram_init_data
from app.core.logger import logger
from app.api.routes.users import build_user_stats

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/validate", response_model=AuthResponse)
async def validate_init_data(
    request: AuthValidateRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_data = validate_telegram_init_data(request.init_data)

        if not user_data:
            return AuthResponse(
                success=False,
                message="Invalid initData"
            )

        user_id = user_data.get("id")
        username = user_data.get("username")
        first_name = user_data.get("first_name")

        user = await UserCRUD.get_or_create(
            db,
            user_id=user_id,
            username=username,
            first_name=first_name
        )

        user_stats = await build_user_stats(db, user)

        return AuthResponse(
            success=True,
            user=user_stats,
            message="Authentication successful"
        )

    except Exception as e:
        logger.error(f"Error validating initData: {e}")
        return AuthResponse(
            success=False,
            message="Authentication failed"
        )


@router.post("/init", response_model=InitResponse)
async def init_app(
    request: AuthValidateRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        user_data = validate_telegram_init_data(request.init_data)

        if not user_data:
            return InitResponse(success=False, message="Invalid initData")

        user = await UserCRUD.get_or_create(
            db,
            user_id=user_data.get("id"),
            username=user_data.get("username"),
            first_name=user_data.get("first_name")
        )

        user_stats = await build_user_stats(db, user)

        videos = await VideoCRUD.get_user_videos(
            db, user_id=user.id, limit=100, media_type="video"
        )

        from sqlalchemy import select
        from app.db.models import Video
        result = await db.execute(
            select(Video)
            .where(Video.user_id == user.id)
            .where(Video.media_type.in_(["forwarded_video", "photo", "voice", "audio"]))
            .order_by(Video.created_at.desc())
            .limit(100)
        )
        media = list(result.scalars().all())

        return InitResponse(
            success=True,
            user=user_stats,
            videos=[VideoResponse.from_orm(v) for v in videos],
            media=[VideoResponse.from_orm(m) for m in media],
        )

    except Exception as e:
        logger.error(f"Error in init: {e}")
        return InitResponse(success=False, message="Init failed")
