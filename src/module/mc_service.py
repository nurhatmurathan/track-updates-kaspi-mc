import asyncio
import math
from typing import Any, List

from aiohttp import ClientSession

from .schemas import ProductMCSchema
from src.common.exceptions import HttpRequestError
from src.core import logger, settings


class KaspiMCService:
    OFFERS_PAGINATE_SIZE = 50

    def __init__(self, session: ClientSession, merchant_id: str):
        self.merchant_id = merchant_id
        self.session = session

    async def fetch_products_by_page(
        self, page: int = 0, available: str = "", sku: str = "", init: bool = False
    ) -> dict[str:Any]:
        params = {
            "m": self.merchant_id,
            "p": page,
            "l": self.OFFERS_PAGINATE_SIZE,
            "a": available,
            "t": sku,
        }
        url = settings.offers_url
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HttpRequestError(url, response.status, await response.text())
            json = await response.json()
        return json["total"] if init else json["data"]

    async def fetch_offers(self, availability: bool = True) -> tuple[dict[str:Any]]:
        available = "true" if availability else "false"
        total = await self.fetch_products_by_page(0, available=available, init=True)
        logger.info("Total products to parse: %d. For merchant: %s", total, self.merchant_id)
        page_count = math.ceil(total / self.OFFERS_PAGINATE_SIZE)

        logger.info("Offers: %s, Total Pages: %s", self.merchant_id, page_count)

        tasks = [self.fetch_products_by_page(page, available=available) for page in range(page_count)]
        return await asyncio.gather(*tasks)

    async def get_validated_products(self) -> List[ProductMCSchema]:
        active_offers = await self.fetch_offers(availability=True)
        archive_offers = await self.fetch_offers(availability=False)
        validated_products = []
        for items in active_offers + archive_offers:
            for item in items:
                # item["merchant_id"] = self.merchant_id
                product = ProductMCSchema.model_validate(item)
                validated_products.append(product)

        return validated_products
