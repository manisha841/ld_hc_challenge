from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.item import Item
from app.schemas.item import ItemCreate, ItemUpdate


class ItemService:
    @staticmethod
    async def get_item(db: AsyncSession, item_id: int) -> Item | None:
        result = await db.execute(
            select(Item).where(Item.id == item_id).options(selectinload(Item.owner))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_item(
        db: AsyncSession, item_data: ItemCreate, owner_id: str
    ) -> Item:
        db_item = Item(
            name=item_data.name,
            description=item_data.description,
            price=item_data.price,
            owner_id=owner_id,
        )
        db.add(db_item)
        await db.commit()
        await db.refresh(db_item)
        return db_item

    @staticmethod
    async def update_item(
        db: AsyncSession, item_id: int, item_data: ItemUpdate, owner_id: str
    ) -> Item:
        item = await ItemService.get_item(db, item_id)
        if not item:
            return None

        update_data = item_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(item, field, value)

        await db.commit()
        await db.refresh(item)
        return item

    @staticmethod
    async def delete_item(db: AsyncSession, item_id: int, owner_id: str) -> bool:
        item = await ItemService.get_item(db, item_id)
        if not item:
            return False

        await db.delete(item)
        await db.commit()
        return True
