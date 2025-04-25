from typing import Optional
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import settings
import jwt
from jwt.exceptions import InvalidTokenError

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            "mock_secret_key", 
            algorithms=settings.AUTH0_ALGORITHMS,
            audience=settings.AUTH0_API_AUDIENCE,
        )
        return payload
    except InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    payload = verify_token(credentials)
    return payload

def check_m2m_permissions(credentials: HTTPAuthorizationCredentials = Security(security), required_permission: str = None) -> bool:
    payload = verify_token(credentials)
    
    if "gty" not in payload or payload["gty"] != "client-credentials":
        return False
    
    client_id = payload.get("azp")
    if not client_id:
        return False
    
    m2m_app = settings.M2M_APPLICATIONS.get(client_id)
    if not m2m_app:
        return False
    
    if required_permission and required_permission not in m2m_app["permissions"]:
        return False
    
    return True 