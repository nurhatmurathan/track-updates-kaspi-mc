from aiohttp import ClientSession, ClientTimeout

from src.common.exceptions import HttpRequestError
from src.core import logger, settings


async def kaspimc_logged_in_session(username: str, password: str, merchant_id: str):
    session = ClientSession(timeout=ClientTimeout(total=30))
    try:
        await login_start_session(session, username, password)
        verified = _verify_merchant(session, merchant_id)
        if not verified:
            raise HttpRequestError(
                "Verification merchant", 200, f"Failed to verify merchat_id - {merchant_id}"
            )

        yield session
    finally:
        await session.close()


# async def get_merchants_services(merchants: Sequence[MarketingMerchant]):
#     for merchant in merchants:
#         try:
#             async for service in get_web_service(merchant.phone, merchant.password, merchant.id):
#                 yield service
#         except KaspiRequestError as e:
#             logger.error("Failed login process on merchant: %s: %s", merchant.id, merchant.merchant_name)
#             logger.error(e)
#


async def login_start_session(session: ClientSession, username: str, password: str):
    # set cookie headers
    async with session.get(settings.auth_cookies_url) as response:
        if response.status != 200:
            raise HttpRequestError(settings.getdata_url, response.status, await response.text())

    credentials = {"_u": username, "_p": password}
    async with session.post(settings.login_url, data=credentials) as response:
        if response.status != 200:
            raise HttpRequestError(settings.login_url, response.status, await response.text())

    logger.info("Login successful merchat - %s", username)


async def _verify_merchant(session: ClientSession, merchant_id: str) -> bool:
    async with session.get(settings.merchants_url) as resp:
        if resp.status != 200:
            raise HttpRequestError(settings.merchants_url, resp.status, await resp.text())
        data = await resp.json()
    for merchant in data["merchants"]:
        if merchant["uid"] == merchant_id:
            logger.info("KaspiMC Merchat is verified - %s", merchant_id)
            return True
    return False
