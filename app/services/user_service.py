from typing import Optional, Dict
from utils import load_users
from app.core.security import verify_password


class UserService:
    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict]:
        users = load_users()
        for user in users.values():
            if user["email"] == email:
                return user
        return None

    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[Dict]:
        users = load_users()
        return users.get(user_id)

    @staticmethod
    def verify_user_credentials(email: str, password: str) -> Optional[Dict]:
        user = UserService.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user["hashed_password"]):
            return None
        return user
