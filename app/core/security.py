from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Optional
from datetime import datetime, timedelta
import httpx
from passlib.context import CryptContext

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
import base64

import jwt
from jwt.exceptions import InvalidTokenError

AUTH0_DOMAIN: str = "dev-g1fkrxywfwaxnmmg.us.auth0.com"
AUTH0_API_AUDIENCE: str = "https://dev-g1fkrxywfwaxnmmg.us.auth0.com/api/v2/"
AUTH0_ALGORITHMS: list = ["RS256"]
JWKS_URL: str = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
SECRET_KEY: str = "your-secret-key"
ALGORITHM: str = "HS256"
M2M_CLIENT_ID: str = "UiCirtVTsAhNUlD1IgUhxBGHx7JYPYr8"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
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
                    # Properly construct RSA public key
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
    except jwt.JWTError as e:
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
) -> Dict:
    """
    Returns:
    - For M2M: {'is_m2m': True, 'client_id': '...'}
    - For users: {'user_id': '...', 'is_m2m': False}
    """
    token = credentials.credentials

    try:
        payload = await verify_local_token(token)
        return {"user_id": payload["sub"], "is_m2m": False}
    except HTTPException:
        pass

    try:
        payload = await verify_auth0_token(token)
        print("i am here in verify_auth0_token", payload)

        if payload.get("gty") == "client-credentials":
            return {"is_m2m": True, "client_id": payload.get("sub")}
        else:
            return {"user_id": payload["sub"], "is_m2m": False}
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_owner_access(current_user: dict, owner_id: str) -> None:
    """Verify the current user is the owner of the resource"""
    if current_user["is_m2m"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="M2M clients cannot perform owner operations",
        )
    if current_user["user_id"] != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the owner of this resource",
        )
