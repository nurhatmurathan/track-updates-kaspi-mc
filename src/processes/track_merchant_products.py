from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import HttpRequestError
from src.core import logger
from src.module import KaspiMCService, RepoService, get_repo_service, kaspimc_logged_in_session


async def track_merchant_products_process(db_session: AsyncSession):
    repo_service = get_repo_service(db_session)
    merchants = await repo_service.get_merchants()

    if not merchants:
        logger.warning("No Merchants found in Database")
        return False

    for merchant in merchants:
        try:
            async for http_session in kaspimc_logged_in_session(
                merchant.username, merchant.password, merchant.merchant_id
            ):
                mc_service = KaspiMCService(http_session, merchant.merchant_id)
                await track_merchant_products_process_2(repo_service, mc_service)
        except HttpRequestError as e:
            logger.error("Failed login process on merchant: %s: %s", merchant.merchant_id, merchant.username)
            logger.exception(e)

    return True


async def track_merchant_products_process_2(repo_service: RepoService, mc_service: KaspiMCService):
    merchant_products = await mc_service.get_validated_products()

    for merchant_product in merchant_products:
        await repo_service.track_product(merchant_product, mc_service.merchant_id)
