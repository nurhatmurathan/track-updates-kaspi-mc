from typing import List, Optional

from pydantic import BaseModel, Field


class ProductMCSchema(BaseModel):
    sku: str
    master_sku: str = Field(alias="masterSku")
    title: Optional[str] = None
    master_title: str = Field(alias="masterTitle")
    shop_link: str = Field(alias="shopLink")
    available: bool
    brand: Optional[str] = None
    min_price: Optional[int] = Field(None, alias="minPrice")
    max_price: Optional[int] = Field(None, alias="maxPrice")
    images: Optional[List[str]] = []
    merchant_id: str
