from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import AsyncSessionLocal
from app.db.crud import UserCRUD, VideoCRUD
from app.core.config import settings

router = Router()


@router.message(Command("stats"))
@router.callback_query(F.data == "stats")
async def cmd_stats(event):
    message = event.message if isinstance(event, CallbackQuery) else event
    user_id = event.from_user.id

    async with AsyncSessionLocal() as db:
        user = await UserCRUD.get_by_id(db, user_id)

        if not user:
            await message.answer("Пользователь не найден. Нажмите /start.")
            return

        storage_gb = user.max_storage_mb / 1024
        used_gb = user.used_storage_mb / 1024
        storage_percent = (user.used_storage_mb / user.max_storage_mb * 100) if user.max_storage_mb > 0 else 0

        referral_link = f"https://t.me/{(await event.bot.me()).username}?start=ref_{user_id}"

        stats_text = (
            f"<b>Статистика</b>\n\n"
            f"Хранилище: {used_gb:.2f} / {storage_gb:.0f} ГБ ({storage_percent:.0f}%)\n"
            f"Видео: {user.video_count}\n\n"
            f"Пригласите друга и получите +{settings.REFERRAL_BONUS_MB // 1024} ГБ:\n"
            f"<code>{referral_link}</code>"
        )

        if isinstance(event, CallbackQuery):
            await event.answer()
            await message.edit_text(stats_text)
        else:
            await message.answer(stats_text)


@router.message(Command("myvideos"))
@router.callback_query(F.data == "myvideos")
async def cmd_myvideos(event):
    message = event.message if isinstance(event, CallbackQuery) else event
    user_id = event.from_user.id

    async with AsyncSessionLocal() as db:
        videos = await VideoCRUD.get_user_videos(db, user_id, limit=20)

        if not videos:
            text = "У вас пока нет видео. Нажмите /start, чтобы загрузить первое."
            if isinstance(event, CallbackQuery):
                await event.answer()
                await message.edit_text(text)
            else:
                await message.answer(text)
            return

        text = "<b>Ваши видео:</b>\n\n"
        for i, video in enumerate(videos, 1):
            line = f"{i}. <b>{video.title}</b> — {video.size_mb:.1f} МБ"
            if video.duration:
                minutes = video.duration // 60
                seconds = video.duration % 60
                line += f" ({minutes}:{seconds:02d})"
            text += line + "\n"

        text += f"\nВсего: {len(videos)}"

        if isinstance(event, CallbackQuery):
            await event.answer()
            await message.edit_text(text)
        else:
            await message.answer(text)


@router.callback_query(F.data == "help")
async def callback_help(callback: CallbackQuery):
    await callback.answer()
    from app.bot.handlers.start import cmd_help
    await cmd_help(callback.message)
