from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class UserStats(BaseModel):
    user_id: int
    daily_uploaded_mb: float
    daily_limit_mb: float
    daily_percentage: float
    video_count: int
    referral_link: str
    referral_count: int
    referral_max: int
    referral_bonus_mb: float
    is_referred: bool
    daily_streamed_mb: float = 0.0
    daily_stream_limit_mb: float = 3072.0

    class Config:
        from_attributes = True


class VideoBase(BaseModel):
    title: str
    size_mb: float
    duration: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None


class VideoCreate(VideoBase):
    pass


class VideoRenameRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)


class VideoResponse(VideoBase):
    id: int
    file_id: str
    thumbnail_file_id: Optional[str] = None
    mime_type: Optional[str] = None
    media_type: Optional[str] = "video"
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class VideoListResponse(BaseModel):
    videos: List[VideoResponse]
    total: int
    limit: int
    offset: int


class UploadResponse(BaseModel):
    success: bool
    message: str
    video: Optional[VideoResponse] = None


class AuthValidateRequest(BaseModel):
    init_data: str


class AuthResponse(BaseModel):
    success: bool
    user: Optional[UserStats] = None
    message: Optional[str] = None


class InitResponse(BaseModel):
    success: bool
    user: Optional[UserStats] = None
    videos: List[VideoResponse] = []
    media: List[VideoResponse] = []
    message: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    database: bool
    redis: bool
    bot_api: bool
