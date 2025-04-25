from typing import Optional
from fastapi import HTTPException
from app.models.item import items_db, Item
from app.schemas.item import ItemUpdate


class ItemService:
    @staticmethod
    def get_item(item_id: int) -> Optional[Item]:
        return items_db.get(item_id)

    @staticmethod
    def update_item(item_id: int, item: ItemUpdate, owner_id: str) -> Item:
        if item_id not in items_db:
            raise HTTPException(status_code=404, detail="Item not found")

        existing_item = items_db[item_id]
        if existing_item.owner_id != owner_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        updated_item = Item(id=item_id, **item.model_dump(), owner_id=owner_id)
        items_db[item_id] = updated_item
        return updated_item
