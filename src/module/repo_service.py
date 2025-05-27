from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession

from src.core import logger
from src.core.abstract import Repository
from src.core.models import MCMerchant, MerchantProductAvailabilityTrack, MerchantProductTrack, ProductFeature
from src.module.schemas import (
    ProductEditDetailSchema,
    ProductFeatureSchema,
    ProductMCAvailabilitySchema,
    ProductMCSchema,
)


class RepoService:
    def __init__(
        self,
        session: AsyncSession,
        merchant_repo: Repository[MCMerchant],
        merchant_product_repo: Repository[MerchantProductTrack],
        availability_repo: Repository[MerchantProductAvailabilityTrack],
        product_feature_repo: Repository[ProductFeature],
    ):
        self.session = session
        self.merchant_repo = merchant_repo
        self.merchant_product_repo = merchant_product_repo
        self.availability_repo = availability_repo
        self.product_feature_repo = product_feature_repo

    async def get_merchants(self) -> Sequence[MCMerchant]:
        query = self.merchant_repo.get_list_query()
        result = await self.session.execute(query)
        return result.scalars().all()

    async def track_product(
        self, product_schema: ProductMCSchema, merchant_id: str, kaspi_merchant_id: str, video_id: str = None
    ):
        if product_schema.availabilities:
            for availability in product_schema.availabilities:
                await self.track_availability(availability, product_schema.sku, merchant_id)

        where = [
            MerchantProductTrack.kaspi_merchant_id == kaspi_merchant_id,
            MerchantProductTrack.sku == product_schema.sku,
        ]
        product = await self.merchant_product_repo.get_last_by_filters(where)
        if not product:
            await self.create_product(product_schema, video_id, merchant_id, kaspi_merchant_id)
            return

        if (
            product.title == product_schema.title
            and product.master_title == product_schema.master_title
            and product.shop_link == product_schema.shop_link
            and product.available == product_schema.available
            and product.model == product_schema.model
            and product.brand == product_schema.brand
            and product.video == video_id
            and product.vertical_category == product_schema.vertical_category
            and product.master_category == product_schema.master_category
            and product.min_price == product_schema.min_price
            and product.max_price == product_schema.max_price
            and product.images == product_schema.images
            and product.any_pickup == product_schema.any_pickup
            and product.any_kaspi_delivery == product_schema.any_kaspi_delivery
            and product.any_kaspi_delivery_local == product_schema.any_kaspi_delivery_local
            and product.any_kaspi_delivery_express == product_schema.any_kaspi_delivery_express
            and product.any_merchant_delivery == product_schema.any_merchant_delivery
        ):
            return

        await self.create_product(product_schema, video_id, merchant_id, kaspi_merchant_id)

    async def create_product(
        self, product_schema: ProductMCSchema, video_id: str, merchant_id: str, kaspi_merchant_id: str
    ):
        logger.info("Merchant(%s) Detected update for product: %s", kaspi_merchant_id, product_schema.sku)
        product = MerchantProductTrack(
            **product_schema.model_dump(),
            video=video_id,
            merchant_id=merchant_id,
            kaspi_merchant_id=kaspi_merchant_id,
        )
        await self.merchant_product_repo.create(product, False)

    async def track_product_specifications(self, product_edit_detail_schema: ProductEditDetailSchema):
        for classification in product_edit_detail_schema.classifications:
            for feature in classification.features:
                await self.track_product_feature(
                    feature, classification.code, classification.name, product_edit_detail_schema.code
                )

    async def track_product_feature(
        self, feature_schema: ProductFeatureSchema, class_code, class_name, product_id
    ):
        where = [
            ProductFeature.product_id == product_id,
            ProductFeature.class_code == class_code,
            ProductFeature.attribute_code == feature_schema.attribute_code,
        ]
        latest_feature = await self.product_feature_repo.get_last_by_filters(where)

        if not latest_feature:
            await self.create_product_feature(feature_schema, class_code, class_name, product_id)
            return

        if (
            latest_feature.name == feature_schema.name
            and latest_feature.mandatory == feature_schema.mandatory
            and latest_feature.manufacturer_sku == feature_schema.manufacturer_sku
            and latest_feature.use_for_matching == feature_schema.use_for_matching
            and latest_feature.position == feature_schema.position
            and latest_feature.attribute_type == feature_schema.attribute_type
            and latest_feature.value == feature_schema.value
        ):
            return

        await self.create_product_feature(feature_schema, class_code, class_name, product_id)

    async def create_product_feature(
        self, feature_schema: ProductFeatureSchema, class_code, class_name, product_id
    ):
        logger.info(
            "Detected update for master-product(%s) specification: %s",
            product_id,
            feature_schema.attribute_code,
        )
        product_feature = ProductFeature(
            **feature_schema.model_dump(), product_id=product_id, class_code=class_code, class_name=class_name
        )
        await self.product_feature_repo.create(product_feature, False)

    async def track_availability(self, schema: ProductMCAvailabilitySchema, sku: str, merchant_id: str):
        where = [
            MerchantProductAvailabilityTrack.merchant_id == merchant_id,
            MerchantProductAvailabilityTrack.sku == sku,
            MerchantProductAvailabilityTrack.store_id == schema.store_id,
        ]
        instance = await self.availability_repo.get_last_by_filters(where)
        if not instance:
            await self.create_availability(schema, sku, merchant_id)
            return

        if (
            schema.stock_count == instance.stock_count
            and schema.available == instance.available
            and schema.pre_order == instance.pre_order
            and schema.stock_enabled == instance.stock_enabled
        ):
            return

        await self.create_availability(schema, sku, merchant_id)

    async def create_availability(self, schema: ProductMCAvailabilitySchema, sku: str, merchant_id: str):
        availability = MerchantProductAvailabilityTrack(
            **schema.model_dump(), sku=sku, merchant_id=merchant_id
        )
        await self.availability_repo.create(availability, False)
        logger.info(
            "Merchant(%s) Track availability: %s, %s. Stock: %d",
            merchant_id,
            sku,
            schema.store_id,
            schema.stock_count,
        )
