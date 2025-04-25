from pydantic import BaseModel


class Item(BaseModel):
    id: int
    name: str
    description: str | None = None
    owner_id: str
    price: float


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    owner_id: str | None = None
    price: float | None = None
