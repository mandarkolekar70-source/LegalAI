from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

MAX_BCRYPT_BYTES = 72

def _normalize_password(password: str) -> str:
    # bcrypt works on bytes; ensure <= 72 bytes
    pwd_bytes = password.encode("utf-8")
    if len(pwd_bytes) > MAX_BCRYPT_BYTES:
        pwd_bytes = pwd_bytes[:MAX_BCRYPT_BYTES]
    return pwd_bytes.decode("utf-8", errors="ignore")

def get_password_hash(password: str) -> str:
    password = _normalize_password(password)
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    password = _normalize_password(password)
    return pwd_context.verify(password, hashed)

def create_access_token(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
