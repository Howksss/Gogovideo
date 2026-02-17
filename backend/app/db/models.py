from sqlalchemy import Column, BigInteger, String, Integer, Float, DateTime, Date, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String, nullable=True, index=True)
    first_name = Column(String, nullable=True)
    used_storage_mb = Column(Float, default=0.0)
    max_storage_mb = Column(Integer, default=3072)
    video_count = Column(Integer, default=0)
    max_videos = Column(Integer, default=999999)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    referred_by = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    referral_count = Column(Integer, default=0)
    daily_streamed_bytes = Column(BigInteger, default=0)
    daily_stream_reset_date = Column(Date, nullable=True)

    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")
    usage_stats = relationship("UsageStat", back_populates="user")

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username})>"

    def can_upload_daily(self, file_size_mb: float, today_uploaded_mb: float, daily_limit_mb: float) -> tuple[bool, str]:
        from app.core.config import settings

        if file_size_mb > settings.MAX_FILE_SIZE_MB:
            return False, f"Файл слишком большой. Максимум: {settings.MAX_FILE_SIZE_MB} МБ"

        remaining = daily_limit_mb - today_uploaded_mb
        if file_size_mb > remaining:
            if remaining <= 0:
                return False, "Дневной лимит исчерпан. Попробуйте завтра после 00:00 МСК"
            return False, f"Дневной лимит почти исчерпан. Осталось: {remaining:.0f} МБ"

        return True, "OK"


class Video(Base):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    file_id = Column(String, unique=True, nullable=False, index=True)
    file_unique_id = Column(String, nullable=False)
    thumbnail_file_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    size_mb = Column(Float, nullable=False)
    duration = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    mime_type = Column(String, nullable=True)
    media_type = Column(String, default="video")
    storage_message_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="videos")
    usage_stats = relationship("UsageStat", back_populates="video")

    __table_args__ = (
        Index('ix_videos_user_created', 'user_id', 'created_at'),
    )

    def __repr__(self):
        return f"<Video(id={self.id}, title={self.title}, user_id={self.user_id})>"


class UsageStat(Base):
    __tablename__ = "usage_stats"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False, index=True)
    action = Column(String, nullable=False)
    video_id = Column(Integer, ForeignKey('videos.id', ondelete='SET NULL'), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    user = relationship("User", back_populates="usage_stats")
    video = relationship("Video", back_populates="usage_stats")

    __table_args__ = (
        Index('ix_usage_stats_user_timestamp', 'user_id', 'timestamp'),
    )

    def __repr__(self):
        return f"<UsageStat(id={self.id}, user_id={self.user_id}, action={self.action})>"
