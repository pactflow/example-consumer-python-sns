from src.product.product import Product, Products


# To try and keep the examples as similar as possible, the service class follows
# the singleton pattern, using the PEP-318 example:
# https://peps.python.org/pep-0318/#examples
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


@singleton
class ProductRepository:
    def __init__(self):
        self.products: Products = {
            "09": Product("09", "CREDIT_CARD", "Gem Visa", "v1"),
            "10": Product("10", "CREDIT_CARD", "28 Degrees", "v1"),
            "11": Product("11", "PERSONAL_LOAN", "MyFlexiPay", "v2"),
        }

    async def fetch_all(self) -> Products:
        return self.products

    async def get_by_id(self, id: str) -> Product:
        return self.products[id]

    async def insert(self, product: Product) -> Products:
        self.products[product.id] = product
        return self.products
