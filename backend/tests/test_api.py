import pytest
from httpx import AsyncClient
from app.main import app
from app.db.models import User
from app.db.crud import UserCRUD


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def test_user(db_session):
    user = await UserCRUD.create(
        db_session,
        user_id=123456789,
        username="testuser",
        first_name="Test User"
    )
    return user


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "database" in data


@pytest.mark.asyncio
async def test_root_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "app" in data
    assert "status" in data


@pytest.mark.asyncio
async def test_auth_validate_invalid_data(client):
    response = await client.post(
        "/api/auth/validate",
        json={"init_data": "invalid_data"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is False


@pytest.mark.asyncio
async def test_videos_list_unauthorized(client):
    response = await client.get("/api/videos")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_stats_unauthorized(client):
    response = await client.get("/api/user/stats")
    assert response.status_code == 401
