from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, check_authorization
from app.core.database import get_db
from app.services.item_service import ItemService
from app.schemas.item import ItemUpdate, ItemCreate, ItemResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ItemResponse)
async def create_item(
    item_data: ItemCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Only owners can create items for themselves"""
    check_authorization(current_user, item_data.owner_id, "create:items")
    return await ItemService.create_item(db, item_data, item_data.owner_id)


@router.get("/{item_id}", response_model=ItemResponse)
async def read_item(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """M2M with read scope can read any item, users can read their own items"""
    item = await ItemService.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    check_authorization(current_user, item.owner_id, "read:items")
    return item


@router.put("/{item_id}", response_model=ItemResponse)
async def update_item(
    item_id: int,
    item_data: ItemUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """M2M with update scope or owners can update items"""
    item = await ItemService.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    check_authorization(current_user, item.owner_id, "update:items")
    updated_item = await ItemService.update_item(db, item_id, item_data, item.owner_id)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Item not found")
    return updated_item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Only owners can delete items (M2M not allowed)"""
    item = await ItemService.get_item(db, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    check_authorization(current_user, item.owner_id, "delete:items")
    if not await ItemService.delete_item(db, item_id, item.owner_id):
        raise HTTPException(status_code=404, detail="Item not found")
