from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
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
    m2m_app = None
    for _, app_data in settings.M2M_APPLICATIONS.items():
        if (
            app_data["app_id"] == m2m_data.app_id
            and app_data["client_id"] == m2m_data.client_id
            and app_data["client_secret"] == m2m_data.client_secret
        ):
            m2m_app = app_data
            break

    if not m2m_app:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": m2m_data.client_id,
            "gty": "client-credentials",
            "azp": m2m_data.client_id,
            "permissions": m2m_app["permissions"],
        },
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}
