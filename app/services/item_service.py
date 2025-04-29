from typing import Optional, Dict
from fastapi import HTTPException
from utils import load_items, save_items
from app.schemas.item import ItemUpdate, ItemCreate


class ItemService:
    @staticmethod
    def get_item(item_id: int) -> Optional[Dict]:
        items = load_items()
        return items.get(str(item_id))

    @staticmethod
    def create_item(item_data: ItemCreate, owner_id: str) -> Dict:
        items = load_items()

        new_id = max((int(k) for k in items.keys()), default=0) + 1

        new_item = {
            "id": new_id,
            "name": item_data.name,
            "description": item_data.description,
            "price": item_data.price,
            "owner_id": owner_id,
        }

        items[str(new_id)] = new_item
        save_items(items)

        return new_item

    @staticmethod
    def update_item(
        item_id: int, item_data: ItemUpdate, owner_id: str, is_m2m: bool = False
    ) -> Dict:
        items = load_items()
        item_key = str(item_id)

        if item_key not in items:
            raise HTTPException(status_code=404, detail="Item not found")

        existing_item = items[item_key]

        if not is_m2m and existing_item["owner_id"] != owner_id:
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

    @staticmethod
    def delete_item(item_id: int, owner_id: str, is_m2m: bool = False) -> Dict:
        items = load_items()
        item_key = str(item_id)

        if item_key not in items:
            raise HTTPException(status_code=404, detail="Item not found")

        existing_item = items[item_key]

        if not is_m2m and existing_item["owner_id"] != owner_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        del items[item_key]
        save_items(items)

        return {
            "message": "Item deleted successfully",
            "item_id": item_id,
            "name": existing_item["name"],
        }
