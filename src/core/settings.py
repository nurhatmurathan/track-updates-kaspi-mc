from pydantic_settings import BaseSettings, SettingsConfigDict

from src.common.enums import LoggingLevelsEnum


class Base(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.local", env_file_encoding="utf-8", extra="ignore")


class Settings(Base):
    LOGGING_LEVEL: LoggingLevelsEnum = LoggingLevelsEnum.NOTSET

    auth_cookies_url: str = "https://mc.shop.kaspi.kz/oauth2/authorization/1"
    login_url: str = "https://idmc.shop.kaspi.kz/api/p/login"
    merchants_url: str = "https://mc.shop.kaspi.kz/s/m"
    offers_url: str = "https://mc.shop.kaspi.kz/bff/offer-view/list"


class DBSettings(Base):
    DB_HOST: str
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    DB_PORT: str = "5432"
    DB_ECHO: bool = False

    @property
    def db_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


settings = Settings()
db_settings = DBSettings()
