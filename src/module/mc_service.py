import asyncio
import math
from typing import Any, List

from aiohttp import ClientSession

from .schemas import ProductEditDetailSchema, ProductMCSchema
from src.common.exceptions import HttpRequestError
from src.core import logger, settings


class KaspiMCService:
    OFFERS_PAGINATE_SIZE = 100

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

        chunk_size, result = 10, []
        for i in range(0, len(tasks), chunk_size):
            res = await asyncio.gather(*tasks[i : i + chunk_size])
            result.extend(res)

        return result

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

    async def fetch_offer_edit_detail(self, master_sku, sku):
        url = settings.offer_edit_detail.format(master_sku=master_sku)
        params = {"m": self.merchant_id, "p": sku}
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HttpRequestError(url, response.status, await response.text())
            data = await response.json()
        return data

    async def get_validated_offer_edit_detail(self, master_sku, sku):
        offer_data = await self.fetch_offer_edit_detail(master_sku, sku)
        return ProductEditDetailSchema.model_validate(offer_data)

    async def fetch_offer_detail(self, sku):
        url = settings.offer_detail
        params = {"m": self.merchant_id, "s": sku}
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                raise HttpRequestError(url, response.status, await response.text())
            data = await response.json()
        return data

    async def get_offer_video_id(self, sku) -> str | None:
        offer_data = await self.fetch_offer_detail(sku)
        return offer_data.get("masterProduct", {}).get("videoId")
