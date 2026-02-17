from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks, Query, Header
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.deps import get_current_user
from app.api.schemas import VideoListResponse, VideoResponse, UploadResponse, VideoRenameRequest
from app.db.base import get_db, AsyncSessionLocal
from app.db.models import User
from app.db.crud import VideoCRUD, UserCRUD, UsageStatCRUD
from app.services.video_processor import VideoProcessor
from app.core.logger import logger
from app.core.config import settings
from app.core.security import validate_telegram_init_data
from app.bot.bot_instance import get_bot
from aiogram.types import FSInputFile, BufferedInputFile
import os

router = APIRouter(prefix="/videos", tags=["videos"])

THUMB_DIR = os.path.join(settings.TEMP_DIR, "thumbs")
os.makedirs(THUMB_DIR, exist_ok=True)


@router.get("", response_model=VideoListResponse)
async def get_videos(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    search: Optional[str] = Query(None),
    media_type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    videos = await VideoCRUD.get_user_videos(
        db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        search=search,
        media_type=media_type
    )

    return VideoListResponse(
        videos=videos,
        total=current_user.video_count,
        limit=limit,
        offset=offset
    )


@router.post("/upload", response_model=UploadResponse)
async def upload_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        file_data = await file.read()
        file_size_mb = len(file_data) / (1024 * 1024)

        today_uploaded = await VideoCRUD.get_daily_uploaded_mb(db, current_user.id)
        daily_limit = UserCRUD.compute_daily_limit_mb(current_user)
        can_upload, message = current_user.can_upload_daily(file_size_mb, today_uploaded, daily_limit)
        if not can_upload:
            return UploadResponse(
                success=False,
                message=message
            )

        processor = VideoProcessor()

        video_path, thumbnail_path, metadata = await processor.process_video(
            file_data,
            file.filename,
            add_watermark=False
        )

        bot = get_bot()

        upload_filename = os.path.splitext(file.filename)[0] + ".mp4"
        with open(video_path, 'rb') as video_file:
            video_input = BufferedInputFile(video_file.read(), filename=upload_filename)

            thumbnail_input = None
            if thumbnail_path and os.path.exists(thumbnail_path):
                with open(thumbnail_path, 'rb') as thumb_file:
                    thumbnail_input = BufferedInputFile(thumb_file.read(), filename="thumb.jpg")

            logger.info(f"Uploading to Telegram: file={file.filename}, size={file_size_mb:.1f}MB, has_thumb={thumbnail_input is not None}")

            message = await bot.send_video(
                chat_id=settings.STORAGE_CHANNEL_ID,
                video=video_input,
                thumbnail=thumbnail_input,
                caption=f"User: {current_user.id}\nFile: {file.filename}",
                duration=metadata.get('duration'),
                width=metadata.get('width'),
                height=metadata.get('height'),
                supports_streaming=True
            )

            tg_thumb = message.video.thumbnail if message.video else None
            logger.info(f"Telegram response: has_video={message.video is not None}, has_thumb={tg_thumb is not None}")

        video = await VideoCRUD.create(
            db,
            user_id=current_user.id,
            file_id=message.video.file_id,
            file_unique_id=message.video.file_unique_id,
            title=file.filename,
            size_mb=file_size_mb,
            storage_message_id=message.message_id,
            thumbnail_file_id=message.video.thumbnail.file_id if message.video.thumbnail else None,
            duration=metadata.get('duration'),
            width=metadata.get('width'),
            height=metadata.get('height'),
            mime_type=file.content_type
        )

        if thumbnail_path and os.path.exists(thumbnail_path):
            import shutil
            local_thumb = os.path.join(THUMB_DIR, f"{video.id}.jpg")
            shutil.copy2(thumbnail_path, local_thumb)
            logger.info(f"Thumbnail saved locally: {local_thumb}")

        await UserCRUD.update_storage(db, current_user.id, file_size_mb, increment=True)

        await UsageStatCRUD.create(db, current_user.id, "upload", video.id)

        background_tasks.add_task(
            processor.cleanup_temp_files,
            video_path,
            thumbnail_path
        )

        logger.info(f"Video uploaded successfully: user={current_user.id}, video={video.id}")

        return UploadResponse(
            success=True,
            message="Video uploaded successfully",
            video=VideoResponse.from_orm(video)
        )

    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.patch("/{video_id}", response_model=VideoResponse)
async def rename_video(
    video_id: int,
    body: VideoRenameRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    video = await VideoCRUD.update_title(db, video_id, current_user.id, body.title)
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    return VideoResponse.from_orm(video)


@router.delete("/{video_id}")
async def delete_video(
    video_id: int,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        video = await VideoCRUD.get_by_id(db, video_id)

        if not video:
            raise HTTPException(status_code=404, detail="Video not found")

        if video.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")

        if video.storage_message_id:
            bot = get_bot()
            try:
                await bot.delete_message(
                    chat_id=settings.STORAGE_CHANNEL_ID,
                    message_id=video.storage_message_id
                )
            except Exception as e:
                logger.warning(f"Error deleting message from storage: {e}")

        local_thumb = os.path.join(THUMB_DIR, f"{video_id}.jpg")
        if os.path.exists(local_thumb):
            os.remove(local_thumb)

        await VideoCRUD.delete(db, video_id, current_user.id)

        await UserCRUD.update_storage(db, current_user.id, video.size_mb, increment=False)

        await UsageStatCRUD.create(db, current_user.id, "delete", video_id)

        logger.info(f"Video deleted: user={current_user.id}, video={video_id}")

        return {"success": True, "message": "Video deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting video: {e}")
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.get("/{video_id}/thumbnail")
async def get_video_thumbnail(video_id: int):
    local_thumb = os.path.join(THUMB_DIR, f"{video_id}.jpg")
    if os.path.exists(local_thumb):
        return FileResponse(
            local_thumb,
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=86400"}
        )

    async with AsyncSessionLocal() as db:
        video = await VideoCRUD.get_by_id(db, video_id)

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    if not video.thumbnail_file_id:
        raise HTTPException(status_code=404, detail="No thumbnail")

    try:
        bot = get_bot()
        file_info = await bot.get_file(video.thumbnail_file_id)
        thumb_path = file_info.file_path

        if thumb_path and os.path.isfile(thumb_path):
            import shutil
            shutil.copy2(thumb_path, local_thumb)
            return FileResponse(
                local_thumb,
                media_type="image/jpeg",
                headers={"Cache-Control": "public, max-age=86400"}
            )

        raise HTTPException(status_code=404, detail="Thumbnail file not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching thumbnail: {e}")
        raise HTTPException(status_code=404, detail="Thumbnail not available")


@router.get("/{video_id}/stream")
async def stream_media(
    video_id: int,
    auth: str = Query(...),
    range_header: Optional[str] = Header(None, alias="Range"),
):
    user_data = validate_telegram_init_data(auth)
    if not user_data:
        logger.warning(f"Stream auth failed for video_id={video_id}")
        raise HTTPException(status_code=401, detail="Invalid auth")

    user_id = user_data.get("id")

    async with AsyncSessionLocal() as db:
        user = await UserCRUD.get_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        video = await VideoCRUD.get_by_id(db, video_id)
        if not video or video.user_id != user_id:
            raise HTTPException(status_code=404, detail="Not found")

        streamed_mb = await UserCRUD.get_daily_streamed_mb(db, user)
        if streamed_mb >= UserCRUD.compute_daily_stream_limit_mb(user):
            raise HTTPException(status_code=429, detail="Дневной лимит просмотра исчерпан")

    bot = get_bot()
    try:
        file_info = await bot.get_file(video.file_id)
    except Exception as e:
        logger.error(f"Stream: bot.get_file failed for {video.file_id}: {e}")
        raise HTTPException(status_code=502, detail="Failed to get file info")

    file_path = file_info.file_path
    if not file_path or not os.path.isfile(file_path):
        logger.error(f"Stream: file not found on disk: {file_path}")
        raise HTTPException(status_code=404, detail="File not found on disk")

    file_size = os.path.getsize(file_path)
    logger.info(f"Stream: video_id={video_id}, type={video.media_type}, path={file_path}, size={file_size}")

    mime = video.mime_type or "application/octet-stream"
    if video.media_type == "photo":
        mime = "image/jpeg"
    elif video.media_type == "voice":
        mime = video.mime_type or "audio/ogg"
    elif video.media_type == "audio":
        mime = video.mime_type or "audio/mpeg"

    start = 0
    end = file_size - 1
    status_code = 200

    if range_header:
        try:
            range_spec = range_header.replace("bytes=", "")
            parts = range_spec.split("-")
            start = int(parts[0]) if parts[0] else 0
            end = int(parts[1]) if parts[1] else file_size - 1
            end = min(end, file_size - 1)
            status_code = 206
        except (ValueError, IndexError):
            pass

    content_length = end - start + 1

    async def file_stream():
        bytes_sent = 0
        try:
            with open(file_path, "rb") as f:
                f.seek(start)
                remaining = content_length
                while remaining > 0:
                    chunk_size = min(64 * 1024, remaining)
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    bytes_sent += len(chunk)
                    remaining -= len(chunk)
                    yield chunk
        finally:
            if bytes_sent > 0:
                logger.info(f"Stream finished: user_id={user_id}, video_id={video_id}, bytes_sent={bytes_sent}")
            else:
                logger.debug(f"Stream cancelled: user_id={user_id}, video_id={video_id}")

    resp_headers = {
        "Accept-Ranges": "bytes",
        "Content-Length": str(content_length),
        "Cache-Control": "no-cache",
    }
    if status_code == 206:
        resp_headers["Content-Range"] = f"bytes {start}-{end}/{file_size}"

    return StreamingResponse(
        file_stream(),
        status_code=status_code,
        media_type=mime,
        headers=resp_headers,
    )
