from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductService:
    @staticmethod
    async def get_product(db: AsyncSession, product_id: int) -> Product | None:
        result = await db.execute(
            select(Product)
            .where(Product.id == product_id)
            .options(selectinload(Product.owner))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def create_product(
        db: AsyncSession, product_data: ProductCreate, owner_id: str
    ) -> Product:
        db_product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            owner_id=owner_id,
        )
        db.add(db_product)
        await db.commit()
        await db.refresh(db_product)
        return db_product

    @staticmethod
    async def update_product(
        db: AsyncSession, product_id: int, product_data: ProductUpdate, owner_id: str
    ) -> Product:
        product = await ProductService.get_product(db, product_id)
        if not product:
            return None

        update_data = product_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        await db.commit()
        await db.refresh(product)
        return product

    @staticmethod
    async def delete_product(db: AsyncSession, product_id: int, owner_id: str) -> bool:
        product = await ProductService.get_product(db, product_id)
        if not product:
            return False

        await db.delete(product)
        await db.commit()
        return True
