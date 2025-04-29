from datetime import datetime
from typing import Optional

from sqlalchemy import ARRAY, UUID, BigInteger, ForeignKey, String, text
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column, relationship


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(self) -> str:
        return f"api_{self.__name__.lower()}"


class BaseDates(Base):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(server_default=text("TIMEZONE('utc', now())"), index=True)
    # updated_at: Mapped[datetime] = mapped_column(
    #     server_default=text("TIMEZONE('utc', now())"),
    #     onupdate=datetime.utcnow,
    # )


class BaseUUIDPK(Base):
    __abstract__ = True
    id: Mapped[UUID] = mapped_column(primary_key=True, server_default=text("uuid_generate_v4()"))


class MCMerchant(BaseUUIDPK, BaseDates):
    username: Mapped[str]
    password: Mapped[str]
    merchant_id: Mapped[str]
    store_name: Mapped[Optional[str]]
    products: Mapped[list["MerchantProductTrack"]] = relationship(
        "MerchantProduct", back_populates="merchant"
    )


class MerchantProductTrack(BaseDates):
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    sku: Mapped[str]
    master_sku: Mapped[str]
    title: Mapped[Optional[str]]
    master_title: Mapped[str]
    shop_link: Mapped[str]
    available: Mapped[bool]
    model: Mapped[Optional[str]]
    brand: Mapped[Optional[str]]
    min_price: Mapped[Optional[int]]
    max_price: Mapped[Optional[int]]
    images: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    updated_at: Mapped[datetime]
    any_pickup: Mapped[Optional[bool]]
    any_kaspi_delivery: Mapped[Optional[bool]]
    any_kaspi_delivery_local: Mapped[Optional[bool]]
    any_kaspi_delivery_express: Mapped[Optional[bool]]
    any_merchant_delivery: Mapped[Optional[bool]]

    merchant_id: Mapped[UUID] = mapped_column(ForeignKey("api_mcmerchant.id"))

    merchant: Mapped["MCMerchant"] = relationship("MCMerchant", back_populates="products")
