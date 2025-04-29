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
        "app3": {
            "app_id": "app3",
            "client_id": "mock_client_id_3",
            "client_secret": "mock_client_secret_3",
            "permissions": ["read:items", "update:items", "create:items"],
        },
        "app4": {
            "app_id": "app4",
            "client_id": "mock_client_id_4",
            "client_secret": "mock_client_secret_4",
            "permissions": [
                "read:items",
                "update:items",
                "create:items",
                "delete:items",
            ],
        },
    }

    class Config:
        case_sensitive = True


settings = Settings()
