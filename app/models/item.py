from typing import Optional
from pydantic import BaseModel

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    owner_id: str
    price: float

# Mock database
items_db = {
    1: Item(id=1, name="Item 1", description="Description 1", owner_id="user1", price=10.99),
    2: Item(id=2, name="Item 2", description="Description 2", owner_id="user2", price=20.99),
    3: Item(id=3, name="Item 3", description="Description 3", owner_id="user1", price=30.99),
} 