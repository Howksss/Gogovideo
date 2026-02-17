import asyncio
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func, text as sa_text
from datetime import datetime, timedelta
from app.db.base import AsyncSessionLocal
from app.db.crud import UserCRUD, VideoCRUD
from app.db.models import User, Video, UsageStat
from app.bot.bot_instance import get_bot
from app.core.config import settings
from app.core.logger import logger

router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_USER_IDS_LIST


def _sz(mb: float) -> str:
    return f"{mb / 1024:.1f} ГБ" if mb >= 1024 else f"{mb:.0f} МБ"


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return

    async with AsyncSessionLocal() as db:
        now = datetime.utcnow()
        day_ago = now - timedelta(days=1)
        week_ago = now - timedelta(days=7)

        total_users = (await db.execute(select(func.count(User.id)))).scalar() or 0
        new_24h = (await db.execute(
            select(func.count(User.id)).where(User.created_at >= day_ago)
        )).scalar() or 0
        new_7d = (await db.execute(
            select(func.count(User.id)).where(User.created_at >= week_ago)
        )).scalar() or 0
        with_content = (await db.execute(
            select(func.count(User.id)).where(User.video_count > 0)
        )).scalar() or 0
        conversion = (with_content / total_users * 100) if total_users else 0

        active_24h = (await db.execute(
            select(func.count(func.distinct(UsageStat.user_id)))
            .where(UsageStat.timestamp >= day_ago)
        )).scalar() or 0
        active_7d = (await db.execute(
            select(func.count(func.distinct(UsageStat.user_id)))
            .where(UsageStat.timestamp >= week_ago)
        )).scalar() or 0

        media_rows = (await db.execute(
            select(Video.media_type, func.count(Video.id))
            .group_by(Video.media_type)
        )).all()
        mc = {mt: cnt for mt, cnt in media_rows}
        total_files = sum(mc.values())

        total_mb = float((await db.execute(
            select(func.coalesce(func.sum(Video.size_mb), 0))
        )).scalar())
        avg_mb = total_mb / with_content if with_content else 0

        reg_rows = (await db.execute(
            select(func.date(User.created_at).label("day"), func.count(User.id).label("cnt"))
            .where(User.created_at >= week_ago)
            .group_by(func.date(User.created_at))
            .order_by(func.date(User.created_at).desc())
        )).all()

        top = (await db.execute(
            select(User.username, User.first_name, User.video_count, User.used_storage_mb)
            .where(User.video_count > 0)
            .order_by(User.used_storage_mb.desc())
            .limit(5)
        )).all()

        db_conns = (await db.execute(sa_text(
            "SELECT count(*) FROM pg_stat_activity WHERE datname = 'telegram_media_bot'"
        ))).scalar() or 0

    reg = []
    for r in reg_rows:
        d = r.day.strftime("%d.%m") if hasattr(r.day, "strftime") else str(r.day)[5:10]
        bar = "\u2593" * min(r.cnt // 10 + 1, 20)
        reg.append(f"  {d}  {bar} <b>{r.cnt}</b>")

    tp = []
    for i, u in enumerate(top, 1):
        name = f"@{u.username}" if u.username else (u.first_name or "—")
        tp.append(f"  {i}. {name} — {u.video_count} шт, {_sz(u.used_storage_mb)}")

    msg = (
        f"<b>GoGoVideo</b>\n"
        f"\n"
        f"<b>Юзеры</b>\n"
        f"  Всего: <b>{total_users}</b>\n"
        f"  Новых за 24ч: <b>{new_24h}</b> | за 7д: <b>{new_7d}</b>\n"
        f"  С контентом: <b>{with_content}</b> ({conversion:.0f}%)\n"
        f"\n"
        f"<b>Активность</b>\n"
        f"  Действий за 24ч: <b>{active_24h}</b> юз | за 7д: <b>{active_7d}</b> юз\n"
        f"\n"
        f"<b>Файлы</b> — {total_files}\n"
        f"  Видео: {mc.get('video', 0)} | Пересл: {mc.get('forwarded_video', 0)}"
        f" | Фото: {mc.get('photo', 0)}\n"
        f"  Аудио: {mc.get('audio', 0)} | Голос: {mc.get('voice', 0)}\n"
        f"\n"
        f"<b>Хранилище</b>: <b>{_sz(total_mb)}</b>"
        f" (ср. {_sz(avg_mb)} на юзера)\n"
        f"\n"
        f"<b>Регистрации</b>\n" + "\n".join(reg) + "\n"
        f"\n"
        f"<b>Топ</b>\n" + "\n".join(tp) + "\n"
        f"\n"
        f"<i>DB: {db_conns}/200</i>"
    )

    await message.answer(msg)


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if not is_admin(message.from_user.id):
        return

    text = message.text.removeprefix("/broadcast").strip()
    if not text:
        await message.answer(
            "Использование: <code>/broadcast текст сообщения</code>\n\n"
            "Поддерживает HTML-разметку. Пример:\n"
            "<code>/broadcast Проблемы исправлены! Заходите.</code>"
        )
        return

    async with AsyncSessionLocal() as db:
        total = (await db.execute(select(func.count(User.id)))).scalar() or 0

    await message.answer(
        f"Отправить это сообщение <b>{total}</b> юзерам?\n\n"
        f"---\n{text}\n---\n\n"
        f"Отправь /broadcast_confirm чтобы подтвердить"
    )
    _pending_broadcasts[message.from_user.id] = text


_pending_broadcasts: dict[int, str] = {}


@router.message(Command("broadcast_confirm"))
async def cmd_broadcast_confirm(message: Message):
    if not is_admin(message.from_user.id):
        return

    text = _pending_broadcasts.pop(message.from_user.id, None)
    if not text:
        await message.answer("Нет ожидающей рассылки. Сначала /broadcast")
        return

    bot = get_bot()

    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User.id))
        user_ids = [row[0] for row in result.all()]

    sent = 0
    blocked = 0
    failed = 0
    status_msg = await message.answer(f"Рассылка: 0/{len(user_ids)}...")

    for i, uid in enumerate(user_ids):
        try:
            await bot.send_message(uid, text, parse_mode="HTML")
            sent += 1
        except Exception as e:
            err = str(e).lower()
            if "blocked" in err or "deactivated" in err or "not found" in err:
                blocked += 1
            else:
                failed += 1
                logger.warning(f"Broadcast to {uid} failed: {e}")

        if (i + 1) % 25 == 0:
            await asyncio.sleep(1.1)

        if (i + 1) % 50 == 0:
            try:
                await status_msg.edit_text(f"Рассылка: {i + 1}/{len(user_ids)}...")
            except Exception:
                pass

    await status_msg.edit_text(
        f"Рассылка завершена.\n\n"
        f"Доставлено: <b>{sent}</b>\n"
        f"Заблокировали бота: {blocked}\n"
        f"Ошибки: {failed}"
    )


@router.message(Command("addgb"))
async def cmd_addgb(message: Message):
    if not is_admin(message.from_user.id):
        return

    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Использование: /addgb {user_id} {гб}")
        return

    try:
        target_user_id = int(parts[1])
        gb = float(parts[2])
    except ValueError:
        await message.answer("Неверный формат. Пример: /addgb 123456789 5")
        return

    add_mb = int(gb * 1024)

    async with AsyncSessionLocal() as db:
        user = await UserCRUD.add_storage(db, target_user_id, add_mb)

    if not user:
        await message.answer(f"Пользователь {target_user_id} не найден.")
        return

    new_gb = user.max_storage_mb / 1024
    await message.answer(
        f"Добавлено {gb:.0f} ГБ пользователю {target_user_id}.\n"
        f"Новый лимит: {new_gb:.0f} ГБ"
    )


@router.message(Command("cleanup"))
async def cmd_cleanup(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer("Проверяю видео... Это может занять время.")

    bot = get_bot()
    broken_ids = []
    valid_count = 0

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(select(Video))
        all_videos = list(result.scalars().all())

        for video in all_videos:
            try:
                await bot.get_file(video.file_id)
                valid_count += 1
            except Exception as e:
                logger.warning(f"Broken file_id for video {video.id}: {e}")
                broken_ids.append(video.id)

        if broken_ids:
            for vid_id in broken_ids:
                video = await VideoCRUD.get_by_id(db, vid_id)
                if video:
                    await UserCRUD.update_storage(db, video.user_id, video.size_mb, increment=False)
                    await db.delete(video)
            await db.commit()

    await message.answer(
        f"Проверка завершена.\n"
        f"Валидных: {valid_count}\n"
        f"Удалено битых: {len(broken_ids)}"
        + (f"\nID удалённых: {broken_ids}" if broken_ids else "")
    )


@router.message(Command("rethumb"))
async def cmd_rethumb(message: Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer("Обновляю превьюшки...")

    bot = get_bot()
    fixed = 0
    failed = 0

    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        result = await db.execute(
            select(Video).where(Video.thumbnail_file_id.is_(None))
        )
        videos_no_thumb = list(result.scalars().all())

        if not videos_no_thumb:
            await message.answer("Все видео уже имеют превьюшки.")
            return

        for video in videos_no_thumb:
            try:
                file_info = await bot.get_file(video.file_id)
                msg = await bot.send_video(
                    chat_id=settings.STORAGE_CHANNEL_ID,
                    video=video.file_id,
                    caption=f"Re-thumb: video {video.id}"
                )
                if msg.video and msg.video.thumbnail:
                    video.thumbnail_file_id = msg.video.thumbnail.file_id
                    await db.commit()
                    fixed += 1
                else:
                    failed += 1
                try:
                    await bot.delete_message(settings.STORAGE_CHANNEL_ID, msg.message_id)
                except Exception:
                    pass
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Failed to re-thumb video {video.id}: {e}")
                failed += 1

    await message.answer(
        f"Готово.\nОбновлено превьюшек: {fixed}\nНе удалось: {failed}"
    )
