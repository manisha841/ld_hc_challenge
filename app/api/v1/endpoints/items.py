from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user, check_permissions
from app.services.item_service import ItemService
from app.schemas.item import ItemUpdate

router = APIRouter()


def _get_item_or_404(item_id: int) -> dict:
    """Retrieve item or raise 404 if not found."""
    item = ItemService.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.get("/items/{item_id}")
async def read_item(item_id: int, current_user: dict = Depends(get_current_user)):
    item = _get_item_or_404(item_id)
    check_permissions(current_user, item["owner_id"], "read:items")
    return item


@router.put("/items/{item_id}")
async def update_item(
    item_id: int, item_data: ItemUpdate, current_user: dict = Depends(get_current_user)
):
    item = _get_item_or_404(item_id)
    is_m2m = current_user.get("gty") == "client-credentials"

    check_permissions(
        current_user, item["owner_id"], "update:items" if is_m2m else "read:items"
    )

    return ItemService.update_item(
        item_id=item_id,
        item_data=item_data,
        owner_id=current_user.get("sub"),
        is_m2m=is_m2m,
    )
