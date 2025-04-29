import logging

from .settings import settings

logging.basicConfig(
    level=settings.LOGGING_LEVEL.value,
    encoding="utf-8",
    datefmt="%Y-%m-%d %H:%M:%S",
    format="%(asctime)s [%(levelname)s] %(filename)s - %(funcName)s(): %(message)s",
)
logger = logging.getLogger(__name__)
