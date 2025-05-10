import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import HttpRequestError
from src.core import logger
from src.core.models import MCMerchant
from src.module import KaspiMCService, RepoService, get_repo_service, kaspimc_logged_in_session


async def track_merchant_products_process(db_session: AsyncSession):
    repo_service = get_repo_service(db_session)
    merchants = await repo_service.get_merchants()

    if not merchants:
        logger.warning("No Merchants found in Database")
        return False

    loop = True
    while loop:
        for merchant in merchants:
            logger.info("Start tracking products of merchant %s", merchant.merchant_id)

            try:
                async for http_session in kaspimc_logged_in_session(
                    merchant.username, merchant.password, merchant.merchant_id
                ):
                    mc_service = KaspiMCService(http_session, merchant.merchant_id)
                    await track_merchant_products_process_2(repo_service, mc_service, merchant)
            except HttpRequestError as e:
                logger.error(
                    "Failed login process on merchant: %s: %s", merchant.merchant_id, merchant.username
                )
                logger.exception(e)
            except Exception as e:
                logger.error("Error occurred on merchant: %s: %s", merchant.merchant_id, e)
                # logger.exception(e)
                loop = False

        logger.info("track_merchant_products_process(): Sleeping for 5 hours")
        await asyncio.sleep(3600 * 5)


async def track_merchant_products_process_2(
    repo_service: RepoService, mc_service: KaspiMCService, merchant: MCMerchant
):
    merchant_products = await mc_service.get_validated_products()

    for merchant_product in merchant_products:
        await repo_service.track_product(merchant_product, merchant.id, merchant.merchant_id)
