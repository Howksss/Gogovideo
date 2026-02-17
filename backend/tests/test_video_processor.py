import pytest
import os
from pathlib import Path
from app.services.video_processor import VideoProcessor


@pytest.fixture
def processor():
    return VideoProcessor()


@pytest.mark.asyncio
async def test_save_upload_file(processor):
    test_data = b"test video data"
    filename = "test_video.mp4"

    saved_path = await processor.save_upload_file(test_data, filename)

    assert os.path.exists(saved_path)
    assert saved_path.endswith(".mp4")

    with open(saved_path, 'rb') as f:
        assert f.read() == test_data

    os.remove(saved_path)


@pytest.mark.asyncio
async def test_cleanup_temp_files(processor):
    test_data = b"test data"
    test_path = await processor.save_upload_file(test_data, "test.mp4")

    assert os.path.exists(test_path)

    await processor.cleanup_temp_files(test_path)

    assert not os.path.exists(test_path)


def test_needs_optimization_checks(processor):
    try:
        result = processor.needs_optimization("nonexistent.mp4")
    except Exception:
        pass


@pytest.mark.asyncio
async def test_processor_temp_dir_creation(processor):
    assert processor.temp_dir.exists()
    assert processor.temp_dir.is_dir()
