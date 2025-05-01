from pydantic import UUID4
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import logger
from src.core.abstract import Repository
from src.core.models import MCMerchant, MerchantProductTrack
from src.module.schemas import ProductMCSchema


class RepoService:
    def __init__(
        self,
        session: AsyncSession,
        merchant_repo: Repository[MCMerchant],
        merchant_product_repo: Repository[MerchantProductTrack],
    ):
        self.session = session
        self.merchant_repo = merchant_repo
        self.merchant_product_repo = merchant_product_repo

    async def track_product(self, product_schema: ProductMCSchema, merchant_id: UUID4):
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
