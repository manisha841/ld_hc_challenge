from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user, check_m2m_permissions
from app.services.item_service import ItemService
from app.schemas.item import ItemUpdate, ItemInDB

router = APIRouter()


@router.get("/items/{item_id}", response_model=ItemInDB)
async def read_item(item_id: int, current_user: dict = Depends(get_current_user)):
    item = ItemService.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if user owns the item or if it's an M2M app with read permission
    if item.owner_id != current_user.get("sub") or not await check_m2m_permissions(
        required_permission="read:items"
    ):
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return item


@router.put("/items/{item_id}", response_model=ItemInDB)
async def update_item(
    item_id: int, item: ItemUpdate, current_user: dict = Depends(get_current_user)
):
    # Only allow owners to update items
    if not await check_m2m_permissions(required_permission="update:items"):
        return ItemService.update_item(item_id, item, current_user.get("sub"))

    raise HTTPException(status_code=403, detail="M2M applications cannot update items")
