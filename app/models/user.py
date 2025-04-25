from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: str
    email: EmailStr
    hashed_password: str


users_db = {
    "user1": User(
        id="user1",
        email="user1@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
    ),
    "user2": User(
        id="user2",
        email="user2@example.com",
        hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "password123"
    ),
}
