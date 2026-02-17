from aiogram import Router, F
from aiogram.types import InlineQuery, InlineQueryResultCachedVideo
from app.db.base import AsyncSessionLocal
from app.db.crud import VideoCRUD, UsageStatCRUD
from app.core.logger import logger

router = Router()


@router.inline_query()
async def inline_query_handler(inline_query: InlineQuery):
    try:
        user_id = inline_query.from_user.id
        query_text = inline_query.query.lower().strip()

        async with AsyncSessionLocal() as db:
            videos = await VideoCRUD.get_user_videos(
                db,
                user_id=user_id,
                limit=50,
                search=query_text if query_text else None,
                media_type="video"
            )

            if not videos:
                await inline_query.answer(
                    results=[],
                    cache_time=1,
                    switch_pm_text="Загрузить первое видео",
                    switch_pm_parameter="start"
                )
                return

            results = []
            for video in videos:
                results.append(InlineQueryResultCachedVideo(
                    id=str(video.id),
                    video_file_id=video.file_id,
                    title=video.title,
                    description=f"{video.size_mb:.1f} МБ • {video.duration}с" if video.duration else f"{video.size_mb:.1f} МБ",
                ))

            await inline_query.answer(
                results=results,
                cache_time=1,
                is_personal=True
            )

    except Exception as e:
        logger.error(f"Error handling inline query: {e}")
        try:
            await inline_query.answer(
                results=[],
                cache_time=1,
                switch_pm_text="Произошла ошибка",
                switch_pm_parameter="start"
            )
        except Exception:
            pass


@router.chosen_inline_result()
async def chosen_inline_result_handler(chosen_result):
    try:
        user_id = chosen_result.from_user.id
        video_id = int(chosen_result.result_id)

        async with AsyncSessionLocal() as db:
            await UsageStatCRUD.create(db, user_id, "inline_send", video_id)

        logger.info(f"Inline video sent: user={user_id}, video={video_id}")

    except Exception as e:
        logger.error(f"Error handling chosen inline result: {e}")
