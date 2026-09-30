import datetime
from typing import Union, Any
import jwt
import bcrypt
from app.core.config import settings

def _prep_pwd(password: str) -> bytes:
    """Safely truncate and encode password to 72 bytes for bcrypt."""
    return password.encode('utf-8')[:72]

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify standard password matches hashed password."""
    try:
        return bcrypt.checkpw(_prep_pwd(plain_password), hashed_password.encode('utf-8'))
    except Exception:
        return False

def get_password_hash(password: str) -> str:
    """Hash password using bcrypt directly."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(_prep_pwd(password), salt)
    return hashed.decode('utf-8')

def create_access_token(subject: Union[str, Any], expires_delta: datetime.timedelta = None) -> str:
    """Generate a signed JWT token containing subject claim."""
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Union[str, None]:
    """Decode a JWT access token and return the subject claim."""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload["sub"]
    except jwt.PyJWTError:
        return None
