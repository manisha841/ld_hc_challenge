from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    create_access_token,
)
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.auth import M2MLogin
from app.schemas.user import UserCreate, UserResponse, Token

router = APIRouter()


@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    if await UserService.get_user_by_email(db, user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create new user
    user = await UserService.create_user(db, user_data)
    return user


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)
):
    """Login user and return access token"""
    user = await UserService.authenticate_user(
        db, form_data.username, form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/m2m/login")
async def m2m_login(m2m_data: M2MLogin):
    app_config = settings.M2M_APPLICATIONS.get(m2m_data.app_id)
    if not app_config:
        raise HTTPException(status_code=400, detail="Invalid application ID")

    async with AsyncClient() as client:
        payload = {
            "client_id": app_config["client_id"],
            "client_secret": app_config["client_secret"],
            "audience": settings.AUTH0_API_AUDIENCE,
            "grant_type": "client_credentials",
        }
        headers = {"content-type": "application/json"}

        response = await client.post(
            f"https://{settings.AUTH0_DOMAIN}/oauth/token",
            json=payload,
            headers=headers,
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)

        return response.json()
