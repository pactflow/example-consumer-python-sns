from typing import TypedDict


class Product:
    def __init__(self, id, name, type, version='Unknown'):
        self.id = id
        self.name = name
        self.type = type
        self.version = version


class Products(TypedDict):
    id: str
    product: Product
