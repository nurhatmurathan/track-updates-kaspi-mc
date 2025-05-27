from typing import List, Optional

from pydantic import BaseModel, Field


class ProductMCAvailabilitySchema(BaseModel):
    available: Optional[str] = None
    store_id: Optional[str] = Field(None, alias="storeId")
    stock_count: Optional[int] = Field(None, alias="stockCount")
    pre_order: Optional[int] = Field(None, alias="preOrder")
    stock_enabled: Optional[bool] = Field(None, alias="stockEnabled")
    stock_specified: Optional[bool] = Field(None, alias="stockSpecified")


class ProductMCCityPrice(BaseModel):
    value: int
    city_id: str = Field(alias="cityId")


class ProductMCSchema(BaseModel):
    sku: str
    master_sku: str = Field(alias="masterSku")
    title: Optional[str] = None
    master_title: str = Field(alias="masterTitle")
    shop_link: str = Field(alias="shopLink")
    available: bool
    model: Optional[str] = None
    brand: Optional[str] = None
    vertical_category: Optional[str] = Field(None, alias="verticalCategory")
    master_category: Optional[str] = Field(None, alias="masterCategory")
    min_price: Optional[int] = Field(None, alias="minPrice")
    max_price: Optional[int] = Field(None, alias="maxPrice")
    images: Optional[List[str]] = []
    updated_at: Optional[str] = Field(None, alias="updatedAt")
    any_pickup: Optional[bool] = Field(None, alias="anyPickup")
    any_kaspi_delivery: Optional[bool] = Field(None, alias="anyKaspiDelivery")
    any_kaspi_delivery_local: Optional[bool] = Field(None, alias="anyKaspiDeliveryLocal")
    any_kaspi_delivery_express: Optional[bool] = Field(None, alias="anyKaspiDeliveryExpress")
    any_merchant_delivery: Optional[bool] = Field(None, alias="anyMerchantDelivery")
    availabilities: Optional[List[ProductMCAvailabilitySchema]] = None


class ProductFeatureSchema(BaseModel):
    attribute_code: str = Field(alias="attributeCode")
    name: Optional[str] = None
    # qualifier: Optional[str] = None
    mandatory: Optional[bool] = None
    manufacturer_sku: Optional[bool] = Field(None, alias="manufacturerSku")
    use_for_matching: Optional[bool] = Field(None, alias="useForMatching")
    position: Optional[int] = None
    attribute_type: Optional[str] = Field(alias="attributeType")
    value: Optional[str | int | float | bool | list | dict] = None


class ProductClassificationSchema(BaseModel):
    code: str
    name: str
    features: List[ProductFeatureSchema] = []


class ProductEditDetailSchema(BaseModel):
    code: str
    name: str
    created_at: str = Field(None, alias="createdAt")
    classifications: List[ProductClassificationSchema] = []
