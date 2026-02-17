import asyncio
import random
from aiogram import Router, F
from aiogram.types import (
    Message, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo,
    MessageOriginUser, MessageOriginHiddenUser, MessageOriginChat, MessageOriginChannel,
)
from app.db.base import AsyncSessionLocal
from app.db.crud import VideoCRUD, UserCRUD
from app.core.config import settings
from app.core.logger import logger

router = Router()

_media_group_buffer: dict[str, list[Message]] = {}
_media_group_tasks: dict[str, asyncio.Task] = {}


def _get_sender_title(message: Message) -> str:
    origin = message.forward_origin
    if origin:
        if isinstance(origin, MessageOriginUser):
            name = origin.sender_user.first_name
            if origin.sender_user.last_name:
                name += f" {origin.sender_user.last_name}"
        elif isinstance(origin, MessageOriginHiddenUser):
            name = origin.sender_user_name
        elif isinstance(origin, MessageOriginChannel):
            name = origin.chat.title
        elif isinstance(origin, MessageOriginChat):
            name = origin.sender_chat.title
        else:
            name = message.from_user.first_name
    else:
        name = message.from_user.first_name
    tag = random.randint(100000, 999999)
    return f"{name} #{tag}"


async def _save_media_to_db(message: Message, file_id: str, file_unique_id: str,
                            title: str, size_mb: float, media_type: str,
                            duration: int = None, width: int = None,
                            height: int = None, mime_type: str = None,
                            thumbnail_file_id: str = None):
    user_id = message.from_user.id

    async with AsyncSessionLocal() as db:
        existing = await VideoCRUD.get_by_file_id(db, file_id)
        if existing and existing.user_id == user_id:
            return False

        user = await UserCRUD.get_or_create(
            db, user_id=user_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name
        )

        video = await VideoCRUD.create(
            db,
            user_id=user_id,
            file_id=file_id,
            file_unique_id=file_unique_id,
            title=title,
            size_mb=size_mb,
            storage_message_id=None,
            thumbnail_file_id=thumbnail_file_id,
            duration=duration,
            width=width,
            height=height,
            mime_type=mime_type,
            media_type=media_type
        )

        await UserCRUD.update_storage(db, user_id, size_mb, increment=True)

    logger.info(f"Forwarded {media_type} saved: user={user_id}, video_id={video.id}, title={title}")
    return True


async def _send_reply(message: Message, count: int = 1):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="Открыть GoGoVideo",
            web_app=WebAppInfo(url=settings.WEBAPP_URL)
        )]
    ])
    if count == 1:
        text = "Сохранено! Открой GoGoVideo для просмотра."
    else:
        text = f"Сохранено {count} файлов! Открой GoGoVideo для просмотра."
    await message.reply(text, reply_markup=keyboard)


async def _delayed_group_reply(group_id: str):
    await asyncio.sleep(1.5)
    messages = _media_group_buffer.pop(group_id, [])
    _media_group_tasks.pop(group_id, None)
    if messages:
        await _send_reply(messages[0], count=len(messages))


async def _save_forwarded_media(message: Message, file_id: str, file_unique_id: str,
                                title: str, size_mb: float, media_type: str,
                                duration: int = None, width: int = None,
                                height: int = None, mime_type: str = None,
                                thumbnail_file_id: str = None):
    saved = await _save_media_to_db(
        message, file_id, file_unique_id, title, size_mb, media_type,
        duration, width, height, mime_type, thumbnail_file_id
    )

    if not saved:
        await message.reply("Этот файл уже есть в твоей библиотеке.")
        return

    group_id = message.media_group_id
    if group_id:
        if group_id not in _media_group_buffer:
            _media_group_buffer[group_id] = []
        _media_group_buffer[group_id].append(message)

        old_task = _media_group_tasks.get(group_id)
        if old_task:
            old_task.cancel()
        _media_group_tasks[group_id] = asyncio.create_task(_delayed_group_reply(group_id))
    else:
        await _send_reply(message)


@router.message(F.video)
async def handle_video(message: Message):
    video = message.video
    title = _get_sender_title(message)
    size_mb = round((video.file_size or 0) / (1024 * 1024), 2)
    thumb_id = video.thumbnail.file_id if video.thumbnail else None

    await _save_forwarded_media(
        message,
        file_id=video.file_id,
        file_unique_id=video.file_unique_id,
        title=title,
        size_mb=size_mb,
        media_type="forwarded_video",
        duration=video.duration,
        width=video.width,
        height=video.height,
        mime_type=video.mime_type,
        thumbnail_file_id=thumb_id
    )


@router.message(F.photo)
async def handle_photo(message: Message):
    photo = message.photo[-1]
    title = _get_sender_title(message)
    size_mb = round((photo.file_size or 0) / (1024 * 1024), 2)

    await _save_forwarded_media(
        message,
        file_id=photo.file_id,
        file_unique_id=photo.file_unique_id,
        title=title,
        size_mb=size_mb,
        media_type="photo",
        width=photo.width,
        height=photo.height,
        mime_type="image/jpeg"
    )


@router.message(F.voice)
async def handle_voice(message: Message):
    voice = message.voice
    title = _get_sender_title(message)
    size_mb = round((voice.file_size or 0) / (1024 * 1024), 2)

    await _save_forwarded_media(
        message,
        file_id=voice.file_id,
        file_unique_id=voice.file_unique_id,
        title=title,
        size_mb=size_mb,
        media_type="voice",
        duration=voice.duration,
        mime_type=voice.mime_type or "audio/ogg"
    )


@router.message(F.audio)
async def handle_audio(message: Message):
    audio = message.audio
    title = _get_sender_title(message)
    size_mb = round((audio.file_size or 0) / (1024 * 1024), 2)

    await _save_forwarded_media(
        message,
        file_id=audio.file_id,
        file_unique_id=audio.file_unique_id,
        title=title,
        size_mb=size_mb,
        media_type="audio",
        duration=audio.duration,
        mime_type=audio.mime_type,
        thumbnail_file_id=audio.thumbnail.file_id if audio.thumbnail else None
    )
