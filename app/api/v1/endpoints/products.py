from fastapi import APIRouter, Depends, HTTPException, status
from app.core.security import get_current_user, check_authorization
from app.services.product_service import ProductService
from app.schemas.product import ProductUpdate, ProductCreate

router = APIRouter()


@router.post("/products/", status_code=status.HTTP_201_CREATED)
async def create_product(
    product_data: ProductCreate, current_user: dict = Depends(get_current_user)
):
    """Only owners can create products for themselves"""
    check_authorization(current_user, product_data.owner_id, "create:products")
    return ProductService.create_product(product_data, product_data.owner_id)


@router.get("/products/{product_id}")
async def read_product(product_id: int, current_user: dict = Depends(get_current_user)):
    """M2M with read scope can read any product, users can read their own products"""
    product = ProductService.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    check_authorization(current_user, product["owner_id"], "read:products")
    return product


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: dict = Depends(get_current_user),
):
    """M2M with update scope or owners can update products"""
    product = ProductService.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    check_authorization(current_user, product["owner_id"], "update:products")
    return ProductService.update_product(product_id, product_data, product["owner_id"])


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int, current_user: dict = Depends(get_current_user)
):
    """Only owners can delete products (M2M not allowed)"""
    product = ProductService.get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    check_authorization(current_user, product["owner_id"], "delete:products")
    return ProductService.delete_product(product_id, product["owner_id"])
