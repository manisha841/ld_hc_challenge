from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user, verify_owner_access
from app.services.item_service import ItemService
from app.schemas.item import ItemUpdate, ItemCreate

router = APIRouter()


def _get_item_or_404(item_id: int) -> dict:
    """Retrieve item or raise 404 if not found."""
    if item := ItemService.get_item(item_id):
        return item
    raise HTTPException(status_code=404, detail="Item not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate, current_user: dict = Depends(get_current_user)
):
    """Only owners can create items for themselves"""
    if current_user.get("is_m2m"):
        raise HTTPException(status_code=403, detail="M2M not allowed")
    verify_owner_access(current_user, item_data.owner_id)
    return ItemService.create_item(item_data=item_data, owner_id=item_data.owner_id)


@router.get("/{item_id}")
async def read_item(
    item_id: int,
    current_user: dict = Depends(get_current_user),
):
    """M2M with read scope can read any item, users can read their own items"""
    item = _get_item_or_404(item_id)

    if current_user["is_m2m"]:
        if "read:items" not in current_user.get("scope", "").split():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing required scope: read:items",
            )
        return item

    verify_owner_access(current_user, item["owner_id"])
    return item


@router.put("/{item_id}")
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    current_user: dict = Depends(get_current_user),
):
    """M2M with update scope or owners can update items"""
    item = _get_item_or_404(item_id)

    if current_user["is_m2m"]:
        if "update:items" not in current_user.get("scope", "").split():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing required scope: update:items",
            )
        return ItemService.update_item(item_id, item_data, item["owner_id"])

    verify_owner_access(current_user, item["owner_id"])
    return ItemService.update_item(item_id, item_data, item["owner_id"])


@router.delete("/{item_id}")
async def delete_item(item_id: int, current_user: dict = Depends(get_current_user)):
    """Only owners can delete items (M2M not allowed)"""
    item = _get_item_or_404(item_id)
    if current_user.get("is_m2m"):
        raise HTTPException(status_code=403, detail="M2M not allowed")
    verify_owner_access(current_user, item["owner_id"])
    return ItemService.delete_item(item_id, item["owner_id"])
