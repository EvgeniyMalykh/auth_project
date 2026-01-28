import datetime
import jwt
from django.conf import settings

JWT_SECRET = getattr(settings, "SECRET_KEY", "change-me")
JWT_ALGORITHM = "HS256"
JWT_EXP_SECONDS = 60 * 60  # 1 час


def generate_jwt(user_id: str) -> str:
    now = datetime.datetime.utcnow()
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + datetime.timedelta(seconds=JWT_EXP_SECONDS),
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    return token


def decode_jwt(token: str):
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
