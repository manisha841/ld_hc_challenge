from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float = 0.0


class ProductCreate(ProductBase):
    owner_id: int


class ProductUpdate(ProductBase):
    name: str | None = None
    owner_id: int | None = None


class ProductResponse(ProductBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
