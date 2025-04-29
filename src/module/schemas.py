from datetime import datetime
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
    updated_at: datetime
    any_pickup: Optional[bool] = Field(None, alias="anyPickup")
    any_kaspi_delivery: Optional[bool] = Field(None, alias="anyKaspiDelivery")
    any_kaspi_delivery_local: Optional[bool] = Field(None, alias="anyKaspiDeliveryLocal")
    any_kaspi_delivery_express: Optional[bool] = Field(None, alias="anyKaspiDeliveryExpress")
    any_merchant_delivery: [Optional[bool]] = Field(None, alias="anyMerchantDelivery")
