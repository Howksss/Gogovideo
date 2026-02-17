import pytest
from app.db.crud import UserCRUD, VideoCRUD
from app.db.models import User


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = await UserCRUD.create(
        db_session,
        user_id=123456789,
        username="testuser",
        first_name="Test User"
    )

    assert user.id == 123456789
    assert user.username == "testuser"
    assert user.tier == "free"
    assert user.video_count == 0


@pytest.mark.asyncio
async def test_get_or_create_user(db_session):
    user1 = await UserCRUD.get_or_create(
        db_session,
        user_id=987654321,
        username="newuser"
    )
    assert user1.username == "newuser"

    user2 = await UserCRUD.get_or_create(
        db_session,
        user_id=987654321,
        username="updateduser"
    )
    assert user2.id == user1.id
    assert user2.username == "updateduser"


@pytest.mark.asyncio
async def test_user_can_upload(db_session):
    user = await UserCRUD.create(
        db_session,
        user_id=111222333,
        username="limituser"
    )

    can_upload, message = user.can_upload(100)
    assert can_upload is True

    can_upload, message = user.can_upload(600)
    assert can_upload is False
    assert "Storage limit" in message
