from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.api.schemas import UserStats
from app.db.base import get_db
from app.db.models import User
from app.db.crud import UserCRUD, VideoCRUD, UsageStatCRUD
from app.core.config import settings
from app.core.logger import logger

router = APIRouter(prefix="/user", tags=["user"])


async def build_user_stats(db: AsyncSession, user: User) -> UserStats:
    daily_uploaded = await VideoCRUD.get_daily_uploaded_mb(db, user.id)
    daily_limit = UserCRUD.compute_daily_limit_mb(user)
    daily_pct = (daily_uploaded / daily_limit * 100) if daily_limit > 0 else 0

    referral_count = user.referral_count or 0
    referral_bonus = referral_count * settings.REFERRAL_BONUS_PER_INVITE_MB

    bot_username = settings.BOT_USERNAME

    daily_streamed = await UserCRUD.get_daily_streamed_mb(db, user)

    return UserStats(
        user_id=user.id,
        daily_uploaded_mb=round(daily_uploaded, 1),
        daily_limit_mb=round(daily_limit, 1),
        daily_percentage=round(min(daily_pct, 100), 1),
        video_count=user.video_count,
        referral_link=f"https://t.me/{bot_username}?start=ref_{user.id}",
        referral_count=referral_count,
        referral_max=settings.MAX_REFERRALS,
        referral_bonus_mb=round(referral_bonus, 1),
        is_referred=user.referred_by is not None,
        daily_streamed_mb=round(daily_streamed, 1),
        daily_stream_limit_mb=round(UserCRUD.compute_daily_stream_limit_mb(user), 1),
    )


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await build_user_stats(db, current_user)


@router.get("/usage")
async def get_usage_stats(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stats = await UsageStatCRUD.get_user_stats(db, current_user.id, days)
    return stats


class ActivateReferralRequest(BaseModel):
    code: str


@router.post("/activate-referral")
async def activate_referral(
    body: ActivateReferralRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    if not settings.ENABLE_REFERRAL:
        raise HTTPException(status_code=400, detail="Реферальная система отключена")

    if current_user.referred_by is not None:
        raise HTTPException(status_code=400, detail="Вы уже активировали реферальный код")

    code = body.code.strip()
    if "ref_" in code:
        try:
            ref_id = int(code.split("ref_")[-1].split("&")[0].split("?")[0])
        except (ValueError, IndexError):
            raise HTTPException(status_code=400, detail="Неверный формат кода")
    else:
        raise HTTPException(status_code=400, detail="Неверный формат кода")

    if ref_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя использовать свой код")

    referrer = await UserCRUD.get_by_id(db, ref_id)
    if not referrer:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    if (referrer.referral_count or 0) >= settings.MAX_REFERRALS:
        raise HTTPException(status_code=400, detail="У этого пользователя уже максимум рефералов")

    current_user.referred_by = ref_id
    referrer.referral_count = (referrer.referral_count or 0) + 1
    await db.commit()

    logger.info(f"Referral activated: user={current_user.id} referred_by={ref_id}")

    return await build_user_stats(db, current_user)
