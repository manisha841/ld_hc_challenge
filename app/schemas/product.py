from pydantic import BaseModel


class Product(BaseModel):
    id: int
    name: str
    description: str | None = None
    owner_id: str
    price: float


class ProductCreate(BaseModel):
    name: str
    owner_id: str
    description: str | None = None
    price: float


class ProductUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    owner_id: str | None = None
    price: float | None = None
