from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    name: str
    description: str | None = None
    price: float = 0.0


class ItemCreate(ItemBase):
    owner_id: str


class ItemUpdate(ItemBase):
    name: str | None = None
    owner_id: str | None = None


class ItemResponse(ItemBase):
    id: int
    owner_id: str

    model_config = ConfigDict(from_attributes=True)
