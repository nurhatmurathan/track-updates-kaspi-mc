import logging

from .settings import settings

logging.basicConfig(
    level=settings.LOGGING_LEVEL.value,
    encoding="utf-8",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s [%(levelname)s] %(filename)s - %(funcName)s(): %(message)s",
)
logger = logging.getLogger(__name__)

MC_HEADERS = {
    "sec-ch-ua-platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 "
    "Safari/537.36 Edg/134.0.0.0",
    "Accept": "application/json, text/plain, */*",
    "sec-ch-ua": '"Chromium";v="134", "Not:A-Brand";v="24", "Microsoft Edge";v="134"',
    "Content-Type": "application/json",
    "sec-ch-ua-mobile": "?0",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Host": "idmc.shop.kaspi.kz",
    "Referer": "https://idmc.shop.kaspi.kz/login",
}
