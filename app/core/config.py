from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "FastAPI Auth0 M2M Demo"
    API_V1_STR: str = "/api/v1"

    AUTH0_DOMAIN: str = "your-tenant.auth0.com"
    AUTH0_API_AUDIENCE: str = "https://api.example.com"
    AUTH0_ALGORITHMS: list = ["RS256"]

    M2M_APPLICATIONS: dict = {
        "app1": {
            "app_id": "app1",
            "client_id": "mock_client_id_1",
            "client_secret": "mock_client_secret_1",
            "permissions": ["read:items"],
        },
        "app2": {
            "app_id": "app2",
            "client_id": "mock_client_id_2",
            "client_secret": "mock_client_secret_2",
            "permissions": ["read:items", "update:items"],
        },
    }

    class Config:
        case_sensitive = True


settings = Settings()
