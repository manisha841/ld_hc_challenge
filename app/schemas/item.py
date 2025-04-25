from typing import Optional

from pydantic import BaseModel

class ItemBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float

class ItemCreate(ItemBase):
    pass

class ItemUpdate(ItemBase):
    pass

class ItemInDB(ItemBase):
    id: int
    owner_id: str

    class Config:
        from_attributes = True 