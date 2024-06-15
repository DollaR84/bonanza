from pydantic import BaseModel


class Category(BaseModel):
    name: str
    url: str


class Product(BaseModel):
    id: str
    product_id: str
    title: str
    description: str | None = None
    price: str
    image: str
    url: str
    color: str | None = None
    size: str | None = None


class ProductDetails(BaseModel):
    image: str
    description: str
    color: str | None = None
    size: str | None = None
