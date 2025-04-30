from fastapi import APIRouter, Depends, HTTPException
from app.core.security import get_current_user, verify_owner_access
from app.services.item_service import ItemService
from app.schemas.item import ItemUpdate, ItemCreate
from fastapi import status


router = APIRouter()


def _get_item_or_404(item_id: int) -> dict:
    """Retrieve item or raise 404 if not found."""
    item = ItemService.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# @router.post("/items", status_code=201)
# async def create_item(
#     item_data: ItemCreate, current_user: dict = Depends(get_current_user)
# ):
#     check_permissions(
#         current_user=current_user,
#         item_owner_id=item_data.owner_id,
#         required_permission="create:items",
#     )

#     return ItemService.create_item(item_data=item_data, owner_id=item_data.owner_id)


# @router.get("/items/{item_id}")
# async def read_item(item_id: int, current_user: dict = Depends(get_current_user)):
#     item = _get_item_or_404(item_id)
#     check_permissions(
#         current_user=current_user,
#         item_owner_id=item["owner_id"],
#         required_permission="read:items",
#     )
#     return item


# @router.put("/items/{item_id}")
# async def update_item(
#     item_id: int, item_data: ItemUpdate, current_user: dict = Depends(get_current_user)
# ):
#     item = _get_item_or_404(item_id)
#     is_m2m = current_user.get("gty") == "client-credentials"

#     check_permissions(
#         current_user=current_user,
#         item_owner_id=item["owner_id"],
#         required_permission="update:items",
#     )

#     return ItemService.update_item(
#         item_id=item_id, item_data=item_data, owner_id=item["owner_id"], is_m2m=is_m2m
#     )


# @router.delete("/items/{item_id}")
# async def delete_item(item_id: int, current_user: dict = Depends(get_current_user)):
#     item = _get_item_or_404(item_id)
#     is_m2m = current_user.get("gty") == "client-credentials"

#     check_permissions(
#         current_user=current_user,
#         item_owner_id=item["owner_id"],
#         required_permission="delete:items",
#     )

#     return ItemService.delete_item(
#         item_id=item_id, owner_id=item["owner_id"], is_m2m=is_m2m
#     )


# Router endpoints
@router.post("/items", status_code=status.HTTP_201_CREATED)
async def create_item(
    item_data: ItemCreate, current_user: dict = Depends(get_current_user)
):
    """Only owners can create items for themselves"""
    verify_owner_access(current_user, item_data.owner_id)
    return ItemService.create_item(item_data=item_data, owner_id=item_data.owner_id)


@router.get("/items/{item_id}")
async def read_item(item_id: int, current_user: dict = Depends(get_current_user)):
    """M2M can read any item, users can read their own items"""
    item = _get_item_or_404(item_id)

    # M2M can read anything
    if current_user["is_m2m"]:
        return item

    # Users can only read their own items
    if current_user["user_id"] != item["owner_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only read your own items",
        )
    return item


@router.put("/items/{item_id}")
async def update_item(
    item_id: int, item_data: ItemUpdate, current_user: dict = Depends(get_current_user)
):
    """Only owners can update items"""
    item = _get_item_or_404(item_id)
    verify_owner_access(current_user, item["owner_id"])
    return ItemService.update_item(item_id, item_data)


@router.delete("/items/{item_id}")
async def delete_item(item_id: int, current_user: dict = Depends(get_current_user)):
    """Only owners can delete items"""
    item = _get_item_or_404(item_id)
    verify_owner_access(current_user, item["owner_id"])
    return ItemService.delete_item(item_id)
