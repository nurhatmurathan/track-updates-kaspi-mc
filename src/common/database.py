from asyncio import current_task

# from faststream import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.core import db_settings


class DatabaseService:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )

    def get_scoped_session(self):
        session = async_scoped_session(
            session_factory=self.session_factory,
            scopefunc=current_task,
        )
        return session

    async def scoped_session_dependency(self) -> async_scoped_session[AsyncSession]:
        session = self.get_scoped_session()
        try:
            yield session
        finally:
            await session.close()


db_service = DatabaseService(
    url=db_settings.db_url,
    echo=db_settings.DB_ECHO,
)


# DatabaseSession = Annotated[async_scoped_session[AsyncSession], Depends(db_service.scoped_session_dependency)]
