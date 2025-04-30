from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Auth0 M2M Demo"
    API_V1_STR: str = "/api/v1"

    AUTH0_DOMAIN: str = "dev-g1fkrxywfwaxnmmg.us.auth0.com"
    AUTH0_API_AUDIENCE: str = "https://dev-g1fkrxywfwaxnmmg.us.auth0.com/api/v2/"
    AUTH0_ALGORITHMS: list = ["RS256"]

    M2M_APPLICATIONS: dict = {
        "app1": {
            "app_id": "app1",
            "client_id": "UiCirtVTsAhNUlD1IgUhxBGHx7JYPYr8",
            "client_secret": "jLsrBtvTXVucscwhN0oC9JdXXu3Zt-BXHk9E2zRzSMt6LaK9_9VOgy8pufNt2dcF",
            "grant_type": "client_credentials",
        }
    }

    class Config:
        case_sensitive = True


settings = Settings()
