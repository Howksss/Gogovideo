import hmac
import hashlib
from urllib.parse import parse_qs
from typing import Optional, Dict
from datetime import datetime, timedelta
from jose import JWTError, jwt
from .config import settings


def validate_telegram_init_data(init_data: str) -> Optional[Dict]:
    try:
        parsed_data = parse_qs(init_data)

        received_hash = parsed_data.get('hash', [None])[0]
        if not received_hash:
            return None

        data_check_string_parts = []
        for key in sorted(parsed_data.keys()):
            if key != 'hash':
                value = parsed_data[key][0]
                data_check_string_parts.append(f"{key}={value}")

        data_check_string = '\n'.join(data_check_string_parts)

        secret_key = hmac.new(
            key=b"WebAppData",
            msg=settings.BOT_TOKEN.encode(),
            digestmod=hashlib.sha256
        ).digest()

        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256
        ).hexdigest()

        if calculated_hash != received_hash:
            return None

        auth_date = int(parsed_data.get('auth_date', [0])[0])
        current_time = int(datetime.utcnow().timestamp())
        if current_time - auth_date > 86400:
            return None

        import json
        user_data = json.loads(parsed_data.get('user', ['{}'])[0])

        return user_data

    except Exception as e:
        print(f"Error validating init data: {e}")
        return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[Dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
