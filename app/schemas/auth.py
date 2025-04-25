from typing import Optional
from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class M2MLogin(BaseModel):
    app_id: str
    client_id: str
    client_secret: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: Optional[str] = None
    scopes: list[str] = []
