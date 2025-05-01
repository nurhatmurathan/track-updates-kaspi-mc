from typing import Any, Generic, List, Type, TypeVar

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.models import Base

M = TypeVar("M", bound=Base)


class Repository(Generic[M]):
    model: Type[M] = None  # can be installed in the heir

    def __init__(self, session: AsyncSession, model: Type[M] = None):
        self.session = session
        self.model = model or self.__class__.model
        if self.model is None:
            raise ValueError("Model class must be provided via argument or class attribute.")

    async def get_by_pk(self, instance_id: Any, pk: str = "id") -> M:
        where = [getattr(self.model, pk) == instance_id]
        stmt = select(self.model).filter(*where)
        result = await self.session.execute(stmt)
        return result.scalars().one()

    async def get_by_filters(self, where: list[bool]) -> M:
        stmt = select(self.model).filter(*where)
        result = await self.session.execute(stmt)
        return result.scalars().one()

    async def create(self, instance: M, refresh: bool = True) -> M:
        self.session.add(instance)
        await self.session.commit()
        if refresh:
            await self.session.refresh(instance)
        return instance

    async def create_bulk(self, instances: List[M], refresh: bool = True):
        self.session.add_all(instances)
        await self.session.commit()

        if not refresh:
            return

        for instance in instances:
            await self.session.refresh(instance)

    async def get_or_create(self, instance: M, pk: str = "id") -> M:
        try:
            return await self.get_by_pk(getattr(instance, pk), pk)
        except NoResultFound:
            try:
                return await self.create(instance)
            except IntegrityError:
                await self.session.rollback()
                return await self.get_by_pk(getattr(instance, pk), pk)

    def get_list_query(self):
        return select(self.model)

    async def delete(self, instance: M):
        await self.session.delete(instance)
        await self.session.commit()

    async def update_by_pk(self, instance_id: Any, values: dict[str, Any], pk: str = "id"):
        where = [getattr(self.model, pk) == instance_id]
        stmt = update(self.model).filter(*where).values(**values)
        await self.session.execute(stmt)
        await self.session.commit()
