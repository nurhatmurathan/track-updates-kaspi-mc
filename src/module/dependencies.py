from aiohttp import ClientSession, ClientTimeout
from sqlalchemy.ext.asyncio import AsyncSession

from src.common.exceptions import HttpRequestError
from src.core import logger, settings
from src.core.abstract import Repository
from src.core.models import MCMerchant, MerchantProductAvailability, MerchantProductTrack, ProductFeature
from src.module import RepoService


def get_repo_service(db_session: AsyncSession):
    return RepoService(
        db_session,
        Repository(db_session, MCMerchant),
        Repository(db_session, MerchantProductTrack),
        Repository(db_session, MerchantProductAvailability),
        Repository(db_session, ProductFeature),
    )


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


async def login_start_session(session: ClientSession, username: str, password: str):
    # set cookie headers
    async with session.get(settings.auth_cookies_url) as response:
        if response.status != 200:
            raise HttpRequestError(settings.getdata_url, response.status, await response.text())

    credentials = {"_u": username, "_p": password}
    async with session.post(settings.login_url, data=credentials) as response:
        if response.status != 200:
            raise HttpRequestError(settings.login_url, response.status, await response.text())
        data = await response.json()

    redirect_url = data.get("redirectUrl")  # auth redirect
    async with session.get(redirect_url) as response:
        if response.status != 200:
            raise HttpRequestError(redirect_url, response.status, await response.text())

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
