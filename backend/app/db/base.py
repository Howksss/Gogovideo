from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=60,
    pool_timeout=10,
    pool_use_lifo=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    async with engine.begin() as conn:
        from app.db.models import User, Video, UsageStat
        await conn.run_sync(Base.metadata.create_all)
        from sqlalchemy import text
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS referral_count INTEGER DEFAULT 0"
        ))
        await conn.execute(text(
            "UPDATE users SET referral_count = "
            "(SELECT COUNT(*) FROM users u2 WHERE u2.referred_by = users.id)"
        ))
        await conn.execute(text(
            "ALTER TABLE videos ADD COLUMN IF NOT EXISTS media_type VARCHAR DEFAULT 'video'"
        ))
        await conn.execute(text(
            "ALTER TABLE videos ALTER COLUMN storage_message_id DROP NOT NULL"
        ))
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_streamed_bytes BIGINT DEFAULT 0"
        ))
        await conn.execute(text(
            "ALTER TABLE users ADD COLUMN IF NOT EXISTS daily_stream_reset_date DATE"
        ))


async def close_db():
    await engine.dispose()
