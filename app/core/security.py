from typing import Optional
from datetime import datetime, timedelta
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from app.core.config import settings

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "secret-key-here"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> dict:
    payload = verify_token(credentials)
    return payload


def check_m2m_permissions(
    credentials: HTTPAuthorizationCredentials = Security(security),
    required_permission: str = None,
) -> bool:
    payload = verify_token(credentials)

    if "gty" not in payload or payload["gty"] != "client-credentials":
        return False

    client_id = payload.get("azp")
    if not client_id:
        return False

    m2m_app = settings.M2M_APPLICATIONS.get(client_id)
    if not m2m_app:
        return False

    if required_permission and required_permission not in m2m_app["permissions"]:
        return False

    return True
