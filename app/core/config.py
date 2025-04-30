from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, Any


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Auth0 M2M Demo"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False

    AUTH0_DOMAIN: str = Field(..., env="AUTH0_DOMAIN")
    AUTH0_API_AUDIENCE: str = Field(..., env="AUTH0_API_AUDIENCE")
    AUTH0_ALGORITHMS: list[str] = Field(["RS256"], env="AUTH0_ALGORITHMS")
    AUTH0_M2M_CLIENT_ID: str = Field(..., env="AUTH0_M2M_CLIENT_ID")
    AUTH0_M2M_CLIENT_SECRET: str = Field(..., env="AUTH0_M2M_CLIENT_SECRET")

    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")

    @property
    def JWKS_URL(self) -> str:
        return f"https://{self.AUTH0_DOMAIN}/.well-known/jwks.json"

    @property
    def M2M_APPLICATIONS(self) -> dict[str, Dict[str, Any]]:
        return {
            "app1": {
                "app_id": "app1",
                "client_id": self.AUTH0_M2M_CLIENT_ID,
                "client_secret": self.AUTH0_M2M_CLIENT_SECRET,
                "grant_type": "client_credentials",
            }
        }

    class Config:
        case_sensitive = True
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
