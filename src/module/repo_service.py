from typing import Sequence

from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import logger
from src.core.abstract import Repository
from src.core.models import MCMerchant, MerchantProductAvailability, MerchantProductTrack, ProductFeature
from src.module.schemas import MerchantProductAvailabilitySchema, ProductMCSchema


class RepoService:
    def __init__(
        self,
        session: AsyncSession,
        merchant_repo: Repository[MCMerchant],
        merchant_product_repo: Repository[MerchantProductTrack],
        availability_repo: Repository[MerchantProductAvailability],
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

    async def track_product(self, product_schema: ProductMCSchema, merchant_id: str):
        try:
            where = [
                MerchantProductTrack.merchant_id == merchant_id,
                MerchantProductTrack.sku == product_schema.sku,
                MerchantProductTrack.updated_at == product_schema.updated_at,
            ]  # check for exists latest update
            await self.merchant_product_repo.get_by_filters(where)
        except NoResultFound:
            logger.info("Merchant(%s) Detected update for product: %s", merchant_id, product_schema.sku)
            product = MerchantProductTrack(**product_schema.model_dump())
            await self.merchant_product_repo.create(product, False)

    async def track_availability(self, schema: MerchantProductAvailabilitySchema, sku: str, merchant_id: str):
        where = [
            MerchantProductAvailability.merchant_id == merchant_id,
            MerchantProductAvailability.sku == sku,
        ]
        instance = self.availability_repo.get_last_by_filters(where)
        if not instance:
            await self.create_availability(schema, sku, merchant_id)
            return

        instance_schema = MerchantProductAvailabilitySchema.model_validate(instance)
        if schema == instance_schema:
            await self.create_availability(schema, sku, merchant_id)

    async def create_availability(
        self, schema: MerchantProductAvailabilitySchema, sku: str, merchant_id: str
    ):
        availability = MerchantProductAvailability(**schema.model_dump(), sku=sku, merchant_id=merchant_id)
        await self.availability_repo.create(availability, False)
        logger.info(
            "Merchant(%s) Track availability: %s, %s. Stock: %d",
            merchant_id,
            sku,
            schema.store_id,
            schema.stock_count,
        )
