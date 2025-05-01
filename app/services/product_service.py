from typing import Optional, Dict
from fastapi import HTTPException
from app.schemas.product import ProductUpdate, ProductCreate
from utils import load_products, save_products


class ProductService:
    @staticmethod
    def get_product(product_id: int) -> Optional[Dict]:
        products = load_products()
        return products.get(str(product_id))

    @staticmethod
    def create_product(product_data: ProductCreate, owner_id: str) -> Dict:
        products = load_products()

        new_id = max((int(k) for k in products.keys()), default=0) + 1

        new_product = {
            "id": new_id,
            "name": product_data.name,
            "description": product_data.description,
            "price": product_data.price,
            "owner_id": owner_id,
        }

        products[str(new_id)] = new_product
        save_products(products)

        return new_product

    @staticmethod
    def update_product(
        product_id: int,
        product_data: ProductUpdate,
        owner_id: str,
        is_m2m: bool = False,
    ) -> Dict:
        products = load_products()
        product_key = str(product_id)

        if product_key not in products:
            raise HTTPException(status_code=404, detail="Product not found")

        existing_product = products[product_key]

        if not is_m2m and existing_product["owner_id"] != owner_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        updates = {}
        if product_data.name is not None:
            updates["name"] = product_data.name
        if product_data.description is not None:
            updates["description"] = product_data.description
        if product_data.price is not None:
            updates["price"] = product_data.price
        if product_data.owner_id is not None:
            updates["owner_id"] = product_data.owner_id

        updated_product = {**existing_product, **updates}

        ProductUpdate(**updated_product)

        products[product_key] = updated_product
        save_products(products)

        return updated_product

    @staticmethod
    def delete_product(product_id: int, owner_id: str, is_m2m: bool = False) -> Dict:
        products = load_products()
        product_key = str(product_id)

        if product_key not in products:
            raise HTTPException(status_code=404, detail="Product not found")

        existing_product = products[product_key]

        if not is_m2m and existing_product["owner_id"] != owner_id:
            raise HTTPException(status_code=403, detail="Not enough permissions")

        del products[product_key]
        save_products(products)

        return {
            "message": "Product deleted successfully",
            "product_id": product_id,
            "name": existing_product["name"],
        }
