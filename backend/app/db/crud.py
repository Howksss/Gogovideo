from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, date, timedelta, timezone
from zoneinfo import ZoneInfo
from .models import User, Video, UsageStat
from app.core.config import settings

MSK = ZoneInfo('Europe/Moscow')


class UserCRUD:

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, user_id: int, username: Optional[str] = None,
                     first_name: Optional[str] = None, referred_by: Optional[int] = None) -> User:
        if referred_by == user_id:
            referred_by = None

        user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            used_storage_mb=0.0,
            max_storage_mb=settings.MAX_STORAGE_MB,
            video_count=0,
            max_videos=settings.MAX_VIDEOS,
            referred_by=referred_by,
            referral_count=0
        )

        if referred_by and settings.ENABLE_REFERRAL:
            referrer = await UserCRUD.get_by_id(db, referred_by)
            if referrer and (referrer.referral_count or 0) < settings.MAX_REFERRALS:
                referrer.referral_count = (referrer.referral_count or 0) + 1

        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    def _referral_bonus_mb(user: User) -> float:
        invitee_bonus = settings.REFERRAL_BONUS_INVITEE_MB if user.referred_by else 0
        active_referrals = min(user.referral_count or 0, settings.MAX_REFERRALS)
        inviter_bonus = active_referrals * settings.REFERRAL_BONUS_PER_INVITE_MB
        return invitee_bonus + inviter_bonus

    @staticmethod
    def compute_daily_limit_mb(user: User) -> float:
        return settings.DAILY_UPLOAD_LIMIT_MB + UserCRUD._referral_bonus_mb(user)

    @staticmethod
    def compute_daily_stream_limit_mb(user: User) -> float:
        return settings.DAILY_STREAM_LIMIT_MB + UserCRUD._referral_bonus_mb(user)

    @staticmethod
    async def get_or_create(db: AsyncSession, user_id: int, username: Optional[str] = None,
                            first_name: Optional[str] = None, referred_by: Optional[int] = None) -> User:
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            user = await UserCRUD.create(db, user_id, username, first_name, referred_by)
        else:
            if username and user.username != username:
                user.username = username
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            await db.commit()
            await db.refresh(user)
        return user

    @staticmethod
    async def update_storage(db: AsyncSession, user_id: int, size_mb: float, increment: bool = True):
        user = await UserCRUD.get_by_id(db, user_id)
        if user:
            if increment:
                user.used_storage_mb += size_mb
                user.video_count += 1
            else:
                user.used_storage_mb -= size_mb
                user.video_count -= 1
            await db.commit()

    @staticmethod
    async def add_storage(db: AsyncSession, user_id: int, add_mb: int):
        user = await UserCRUD.get_by_id(db, user_id)
        if user:
            user.max_storage_mb += add_mb
            await db.commit()
            await db.refresh(user)
        return user

    @staticmethod
    async def get_total_users(db: AsyncSession) -> int:
        result = await db.execute(select(func.count(User.id)))
        return result.scalar() or 0

    @staticmethod
    async def get_daily_streamed_mb(db: AsyncSession, user: User) -> float:
        today_msk = datetime.now(MSK).date()
        if user.daily_stream_reset_date != today_msk:
            user.daily_streamed_bytes = 0
            user.daily_stream_reset_date = today_msk
            await db.commit()
        return (user.daily_streamed_bytes or 0) / (1024 * 1024)

    @staticmethod
    async def check_and_update_stream_usage(db: AsyncSession, user: User, bytes_streamed: int) -> bool:
        today_msk = datetime.now(MSK).date()
        if user.daily_stream_reset_date != today_msk:
            user.daily_streamed_bytes = 0
            user.daily_stream_reset_date = today_msk

        limit_bytes = int(UserCRUD.compute_daily_stream_limit_mb(user) * 1024 * 1024)
        if (user.daily_streamed_bytes or 0) + bytes_streamed > limit_bytes:
            return False

        user.daily_streamed_bytes = (user.daily_streamed_bytes or 0) + bytes_streamed
        await db.commit()
        return True

    @staticmethod
    async def get_active_users(db: AsyncSession, days: int) -> int:
        since = datetime.utcnow() - timedelta(days=days)
        result = await db.execute(
            select(func.count(func.distinct(UsageStat.user_id)))
            .where(UsageStat.timestamp >= since)
        )
        return result.scalar() or 0


class VideoCRUD:

    @staticmethod
    async def get_daily_uploaded_mb(db: AsyncSession, user_id: int) -> float:
        now_msk = datetime.now(MSK)
        today_start_msk = now_msk.replace(hour=0, minute=0, second=0, microsecond=0)
        result = await db.execute(
            select(func.coalesce(func.sum(Video.size_mb), 0.0))
            .where(and_(
                Video.user_id == user_id,
                Video.created_at >= today_start_msk
            ))
        )
        return float(result.scalar())

    @staticmethod
    async def create(db: AsyncSession, user_id: int, file_id: str, file_unique_id: str,
                     title: str, size_mb: float, storage_message_id: Optional[int] = None,
                     thumbnail_file_id: Optional[str] = None, duration: Optional[int] = None,
                     width: Optional[int] = None, height: Optional[int] = None,
                     mime_type: Optional[str] = None, media_type: str = "video") -> Video:
        video = Video(
            user_id=user_id,
            file_id=file_id,
            file_unique_id=file_unique_id,
            thumbnail_file_id=thumbnail_file_id,
            title=title,
            size_mb=size_mb,
            duration=duration,
            width=width,
            height=height,
            mime_type=mime_type,
            storage_message_id=storage_message_id,
            media_type=media_type
        )
        db.add(video)
        await db.commit()
        await db.refresh(video)
        return video

    @staticmethod
    async def get_by_id(db: AsyncSession, video_id: int) -> Optional[Video]:
        result = await db.execute(select(Video).where(Video.id == video_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_videos(db: AsyncSession, user_id: int, limit: int = 50,
                              offset: int = 0, search: Optional[str] = None,
                              media_type: Optional[str] = None) -> List[Video]:
        query = select(Video).where(Video.user_id == user_id)

        if media_type:
            query = query.where(Video.media_type == media_type)

        if search:
            query = query.where(Video.title.ilike(f"%{search}%"))

        query = query.order_by(Video.created_at.desc()).limit(limit).offset(offset)

        result = await db.execute(query)
        return list(result.scalars().all())

    @staticmethod
    async def delete(db: AsyncSession, video_id: int, user_id: int) -> bool:
        video = await VideoCRUD.get_by_id(db, video_id)
        if video and video.user_id == user_id:
            await db.delete(video)
            await db.commit()
            return True
        return False

    @staticmethod
    async def update_title(db: AsyncSession, video_id: int, user_id: int, title: str) -> Optional[Video]:
        video = await VideoCRUD.get_by_id(db, video_id)
        if video and video.user_id == user_id:
            video.title = title
            await db.commit()
            await db.refresh(video)
            return video
        return None

    @staticmethod
    async def get_by_file_id(db: AsyncSession, file_id: str) -> Optional[Video]:
        result = await db.execute(select(Video).where(Video.file_id == file_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_total_count(db: AsyncSession) -> int:
        result = await db.execute(select(func.count(Video.id)))
        return result.scalar() or 0

    @staticmethod
    async def get_total_storage(db: AsyncSession) -> float:
        result = await db.execute(select(func.coalesce(func.sum(Video.size_mb), 0)))
        return float(result.scalar())


class UsageStatCRUD:

    @staticmethod
    async def create(db: AsyncSession, user_id: int, action: str, video_id: Optional[int] = None):
        stat = UsageStat(
            user_id=user_id,
            action=action,
            video_id=video_id
        )
        db.add(stat)
        await db.commit()

    @staticmethod
    async def get_user_stats(db: AsyncSession, user_id: int, days: int = 30) -> dict:
        since = datetime.utcnow() - timedelta(days=days)

        result = await db.execute(
            select(UsageStat.action, func.count(UsageStat.id))
            .where(and_(UsageStat.user_id == user_id, UsageStat.timestamp >= since))
            .group_by(UsageStat.action)
        )

        stats = {action: count for action, count in result.all()}

        return {
            "uploads": stats.get("upload", 0),
            "deletes": stats.get("delete", 0),
            "inline_sends": stats.get("inline_send", 0),
            "period_days": days
        }
