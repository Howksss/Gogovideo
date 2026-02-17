from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.db.base import get_db
from app.db.crud import UserCRUD
from app.db.models import User
from app.core.security import validate_telegram_init_data


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db)
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    init_data = authorization.replace("Bearer ", "")

    user_data = validate_telegram_init_data(init_data)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid authorization data")

    user_id = user_data.get("id")
    username = user_data.get("username")
    first_name = user_data.get("first_name")

    user = await UserCRUD.get_or_create(
        db,
        user_id=user_id,
        username=username,
        first_name=first_name
    )

    return user
