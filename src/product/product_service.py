from typing import Dict

from src.product.product import Product, Products
from src.product.product_repository import ProductRepository

repository = ProductRepository()


# Actual message handler, doesn't care about SNS at all!
async def receive_product_update(product: Dict) -> Products:
    return await repository.insert(Product(product['id'], product['type'], product['name']))
