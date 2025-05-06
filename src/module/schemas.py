from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


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


class MerchantProductAvailabilitySchema(BaseModel):
    available: Optional[str]
    store_id: Optional[str] = Field(None, alias="storeId")
    stock_count: Optional[int] = Field(None, alias="stockCount")
    pre_order: Optional[int] = Field(None, alias="preOrder")
    stock_enabled: Optional[bool] = Field(None, alias="stockEnabled")
    stock_specified: Optional[bool] = Field(None, alias="stockSpecified")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
