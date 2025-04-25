from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user
from app.services.item_service import ItemService
from app.schemas.item import ItemUpdate, ItemInDB

router = APIRouter()


def _has_access(
    current_user: dict, item_owner_id: str, required_permission: str
) -> bool:
    if current_user.get("gty") == "client-credentials":
        return required_permission in current_user.get("permissions", [])
    return item_owner_id == current_user.get("sub")


@router.get("/items/{item_id}", response_model=ItemInDB)
async def read_item(item_id: int, current_user: dict = Depends(get_current_user)):
    item = ItemService.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    if not _has_access(current_user, item.owner_id, "read:items"):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return item


@router.put("/items/{item_id}", response_model=ItemInDB)
async def update_item(
    item_id: int, item: ItemUpdate, current_user: dict = Depends(get_current_user)
):
    existing_item = ItemService.get_item(item_id)
    if not existing_item:
        raise HTTPException(status_code=404, detail="Item not found")

    print(
        "has access", _has_access(current_user, existing_item.owner_id, "update:items")
    )

    if not _has_access(current_user, existing_item.owner_id, "update:items"):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return ItemService.update_item(item_id, item, current_user.get("sub"))
