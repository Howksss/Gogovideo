import os
import uuid
import ffmpeg
import aiofiles
from pathlib import Path
from typing import Tuple, Optional, Dict
from app.core.config import settings
from app.core.logger import logger


class VideoProcessor:

    def __init__(self):
        self.temp_dir = Path(settings.TEMP_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.thumb_dir = Path(settings.TEMP_DIR) / "thumbs"
        self.thumb_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload_file(self, file_data: bytes, filename: str) -> str:
        file_id = str(uuid.uuid4())
        file_ext = Path(filename).suffix
        temp_path = self.temp_dir / f"{file_id}{file_ext}"

        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(file_data)

        return str(temp_path)

    def get_video_metadata(self, video_path: str) -> Dict:
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

            if not video_stream:
                raise ValueError("No video stream found")

            metadata = {
                'duration': int(float(probe['format'].get('duration', 0))),
                'width': int(video_stream.get('width', 0)),
                'height': int(video_stream.get('height', 0)),
                'codec': video_stream.get('codec_name', 'unknown'),
                'bitrate': int(probe['format'].get('bit_rate', 0)),
                'size_mb': round(float(probe['format'].get('size', 0)) / (1024 * 1024), 2)
            }

            return metadata

        except Exception as e:
            logger.error(f"Error extracting video metadata: {e}")
            raise

    async def generate_thumbnail(self, video_path: str) -> str:
        thumbnail_path = str(self.temp_dir / f"{uuid.uuid4()}.jpg")

        for seek_time in [1, 0]:
            try:
                (
                    ffmpeg
                    .input(video_path, ss=seek_time)
                    .filter('scale', settings.MAX_THUMBNAIL_SIZE, -1)
                    .output(thumbnail_path, vframes=1, format='image2', vcodec='mjpeg', **{'q:v': '5'})
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )

                if os.path.exists(thumbnail_path) and os.path.getsize(thumbnail_path) > 0:
                    logger.info(f"Thumbnail generated at ss={seek_time}: {thumbnail_path}")
                    return thumbnail_path

            except Exception as e:
                logger.warning(f"Thumbnail generation failed at ss={seek_time}: {e}")
                continue

        logger.error(f"All thumbnail generation attempts failed for: {video_path}")
        return None

    def save_thumbnail_locally(self, thumbnail_path: str, video_id: int) -> str:
        dest = str(self.thumb_dir / f"{video_id}.jpg")
        import shutil
        shutil.copy2(thumbnail_path, dest)
        logger.info(f"Thumbnail saved locally: {dest}")
        return dest

    def _get_rotation(self, video_path: str) -> int:
        try:
            probe = ffmpeg.probe(video_path)
            video_stream = next(
                (s for s in probe['streams'] if s['codec_type'] == 'video'), None
            )
            if not video_stream:
                return 0

            rotation = int(video_stream.get('tags', {}).get('rotate', 0))
            if rotation:
                return rotation

            for sd in video_stream.get('side_data_list', []):
                if sd.get('side_data_type') == 'Display Matrix':
                    rot = int(sd.get('rotation', 0))
                    if rot:
                        return rot

            return 0
        except Exception:
            return 0

    async def remux_to_mp4(self, video_path: str) -> str:
        ext = Path(video_path).suffix.lower()
        rotation = self._get_rotation(video_path)

        if ext == '.mp4' and rotation == 0:
            return video_path

        output_path = str(self.temp_dir / f"{uuid.uuid4()}.mp4")
        try:
            output_kwargs = {'c': 'copy', 'movflags': 'faststart'}
            if rotation != 0:
                output_kwargs['metadata:s:v:0'] = 'rotate=0'
                logger.info(f"Stripping rotation tag ({rotation}°) from {video_path}")

            (
                ffmpeg
                .input(video_path)
                .output(output_path, **output_kwargs)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            logger.info(f"Remuxed {ext} -> .mp4: {video_path} -> {output_path}")
            os.remove(video_path)
            return output_path
        except Exception as e:
            logger.warning(f"Remux failed, using original: {e}")
            if os.path.exists(output_path):
                os.remove(output_path)
            return video_path

    async def cleanup_temp_files(self, *file_paths: str):
        for path in file_paths:
            try:
                if path and os.path.exists(path):
                    os.remove(path)
                    logger.debug(f"Cleaned up temp file: {path}")
            except Exception as e:
                logger.warning(f"Error cleaning up {path}: {e}")

    async def process_video(self, file_data: bytes, filename: str,
                           add_watermark: bool = False) -> Tuple[str, str, Dict]:
        original_path = None
        thumbnail_path = None

        try:
            original_path = await self.save_upload_file(file_data, filename)
            logger.info(f"Saved upload: {original_path}")

            metadata = self.get_video_metadata(original_path)
            logger.info(f"Extracted metadata: {metadata}")

            thumbnail_path = await self.generate_thumbnail(original_path)

            current_path = await self.remux_to_mp4(original_path)

            return current_path, thumbnail_path, metadata

        except Exception as e:
            await self.cleanup_temp_files(original_path, thumbnail_path)
            logger.error(f"Error processing video: {e}")
            raise
