from typing import Optional, Dict
from fastapi import HTTPException
from utils import load_items, save_items
from app.schemas.item import ItemUpdate


class ItemService:
    @staticmethod
    def get_item(item_id: int) -> Optional[Dict]:
        items = load_items()
        return items.get(str(item_id))

    @staticmethod
    def update_item(item_id: int, item_data: ItemUpdate, owner_id: str) -> Dict:
        items = load_items()
        item_key = str(item_id)

        if item_key not in items:
            raise HTTPException(status_code=404, detail="Item not found")

        existing_item = items[item_key]

        if existing_item["owner_id"] != owner_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        updates = {}
        if item_data.name is not None:
            updates["name"] = item_data.name
        if item_data.description is not None:
            updates["description"] = item_data.description
        if item_data.price is not None:
            updates["price"] = item_data.price
        if item_data.owner_id is not None:
            updates["owner_id"] = item_data.owner_id

        updated_item = {**existing_item, **updates}

        ItemUpdate(**updated_item)

        items[item_key] = updated_item
        save_items(items)

        return updated_item
