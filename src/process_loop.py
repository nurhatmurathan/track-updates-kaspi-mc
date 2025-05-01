import asyncio
from datetime import datetime


async def main():
    from src.common.database import db_service
    from src.processes import track_merchant_products_process

    async for session in db_service.scoped_session_dependency():
        async with asyncio.TaskGroup() as group:
            group.create_task(track_merchant_products_process(session))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        now = datetime.utcnow()
        print("Consumer stopped at {}".format(now))  # noqa: T201
