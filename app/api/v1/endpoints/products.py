from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_user, check_authorization
from app.core.database import get_db
from app.services.product_service import ProductService
from app.schemas.product import ProductUpdate, ProductCreate, ProductResponse

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Only owners can create products for themselves"""
    check_authorization(current_user, product_data.owner_id, "create:products")
    return await ProductService.create_product(db, product_data, product_data.owner_id)


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """M2M with read scope can read any product, users can read their own products"""
    product = await ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    check_authorization(current_user, product.owner_id, "read:products")
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """M2M with update scope or owners can update products"""
    product = await ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    check_authorization(current_user, product.owner_id, "update:products")
    updated_product = await ProductService.update_product(
        db, product_id, product_data, product.owner_id
    )
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Only owners can delete products (M2M not allowed)"""
    product = await ProductService.get_product(db, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    check_authorization(current_user, product.owner_id, "delete:products")
    if not await ProductService.delete_product(db, product_id, product.owner_id):
        raise HTTPException(status_code=404, detail="Product not found")
