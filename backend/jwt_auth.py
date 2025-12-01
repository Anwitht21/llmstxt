import jwt
from datetime import datetime, timedelta, timezone
from config import settings

JWT_ALGORITHM = "HS256"
JWT_EXPIRY_MINUTES = 5

def generate_token() -> str:
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(minutes=JWT_EXPIRY_MINUTES),
        "iat": datetime.now(timezone.utc),
        "type": "websocket"
    }
    return jwt.encode(payload, settings.api_key, algorithm=JWT_ALGORITHM)

def validate_token(token: str) -> bool:
    try:
        jwt.decode(token, settings.api_key, algorithms=[JWT_ALGORITHM])
        return True
    except jwt.ExpiredSignatureError:
        return False
    except jwt.InvalidTokenError:
        return False
