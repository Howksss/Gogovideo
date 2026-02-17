from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import Optional, List
import os


class Settings(BaseSettings):
    APP_NAME: str = "GoGoVideo"
    DEBUG: bool = False

    BOT_TOKEN: str
    BOT_API_URL: str = "https://api.telegram.org"
    STORAGE_CHANNEL_ID: int
    WEBAPP_URL: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    REDIS_HOST: str = "redis"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    FRONTEND_URL: str

    MAX_VIDEOS: int = 999999
    MAX_STORAGE_MB: int = 3072
    MAX_FILE_SIZE_MB: int = 2048

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    TEMP_DIR: str = "/tmp/telegram_media_bot"
    MAX_THUMBNAIL_SIZE: int = 320

    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    RATE_LIMIT_UPLOAD_PER_HOUR: int = 10
    RATE_LIMIT_VIDEOS_PER_MINUTE: int = 100

    ENABLE_REFERRAL: bool = True
    REFERRAL_BONUS_MB: int = 1024
    REFERRAL_BONUS_INVITEE_MB: int = 1024
    REFERRAL_BONUS_PER_INVITE_MB: float = 204.8
    MAX_REFERRALS: int = 10

    DAILY_UPLOAD_LIMIT_MB: int = 3072
    DAILY_STREAM_LIMIT_MB: int = 3072

    BOT_USERNAME: str = ""

    ADMIN_USER_IDS: str = ""

    @property
    def ADMIN_USER_IDS_LIST(self) -> List[int]:
        if not self.ADMIN_USER_IDS:
            return []
        return [int(uid.strip()) for uid in self.ADMIN_USER_IDS.split(",") if uid.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

os.makedirs(settings.TEMP_DIR, exist_ok=True)
os.makedirs("logs", exist_ok=True)
