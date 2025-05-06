from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    name: str
    description: str | None = None
    price: float = 0.0


class ProductCreate(ProductBase):
    owner_id: str


class ProductUpdate(ProductBase):
    name: str | None = None
    owner_id: str | None = None


class ProductResponse(ProductBase):
    id: int
    owner_id: str

    model_config = ConfigDict(from_attributes=True)
