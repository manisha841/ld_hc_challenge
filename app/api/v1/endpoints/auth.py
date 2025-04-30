from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from httpx import AsyncClient
from app.core.security import (
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.core.config import settings
from app.services.user_service import UserService
from app.schemas.auth import M2MLogin

router = APIRouter()


@router.post("/login")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = UserService.verify_user_credentials(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["id"], "scopes": form_data.scopes},
        expires_delta=access_token_expires,
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
