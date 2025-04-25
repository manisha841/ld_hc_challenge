from pydantic import BaseModel


class UserLogin(BaseModel):
    email: str
    password: str


class M2MLogin(BaseModel):
    app_id: str
    client_id: str
    client_secret: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str | None = None
    scopes: list[str] | None = []
