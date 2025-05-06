from fastapi import Depends, HTTPException, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
from typing import Dict
from datetime import datetime, timedelta
import httpx
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64

from app.core.config import settings
from app.core.database import get_db
from app.services.user_service import UserService
from jwt.exceptions import InvalidTokenError
import jwt

AUTH0_DOMAIN = settings.AUTH0_DOMAIN
AUTH0_API_AUDIENCE = settings.AUTH0_API_AUDIENCE
AUTH0_ALGORITHMS = settings.AUTH0_ALGORITHMS
JWKS_URL = settings.JWKS_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_auth0_public_key(token: str):
    """Fetch Auth0 public key from JWKS endpoint and properly construct RSA key"""
    async with httpx.AsyncClient() as client:
        try:
            jwks_response = await client.get(JWKS_URL)
            jwks = jwks_response.json()

            unverified_header = jwt.get_unverified_header(token)

            for key in jwks["keys"]:
                if key["kid"] == unverified_header["kid"]:
                    n = int.from_bytes(base64.urlsafe_b64decode(key["n"] + "=="), "big")
                    e = int.from_bytes(base64.urlsafe_b64decode(key["e"] + "=="), "big")
                    public_numbers = rsa.RSAPublicNumbers(e, n)
                    return public_numbers.public_key(default_backend())

            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to find matching JWK",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Failed to fetch JWKS",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e


async def verify_auth0_token(token: str) -> dict:
    """Verify Auth0 issued token (either user or M2M)"""
    try:
        rsa_key = await get_auth0_public_key(token)

        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=AUTH0_ALGORITHMS,
            audience=AUTH0_API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
        )
        return payload
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Auth0 token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_local_token(token: str) -> Dict:
    """Verify locally issued JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid local token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Dict:
    """
    Returns:
    - For M2M: {'is_m2m': True, 'client_id': '...', 'scope': '...'}
    - For users: {'id': '...', 'email': '...', 'is_m2m': False}
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Convert user_id to integer since that's what our database expects
        try:
            user_id_int = int(user_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user ID format",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await UserService.get_user(db, user_id_int)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return {"id": user.id, "email": user.email, "is_m2m": False}
    except InvalidTokenError:
        try:
            payload = await verify_auth0_token(token)
            if payload.get("gty") == "client-credentials":
                return {
                    "is_m2m": True,
                    "client_id": payload.get("sub"),
                    "scope": payload.get("scope", ""),
                }
            return {
                "id": payload["sub"],
                "email": payload.get("email"),
                "is_m2m": False,
            }
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            ) from e


def check_authorization(
    current_user: dict, resource_owner_id: str, required_scope: str
) -> None:
    """Check if the current user has permission to access the resource."""
    is_m2m = current_user.get("is_m2m", False)

    if is_m2m:
        if required_scope not in current_user.get("scope", "").split():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
    elif current_user["id"] != resource_owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
