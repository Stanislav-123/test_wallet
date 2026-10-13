import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.database import DATABASE_URL


async def wait_for_db() -> None:
    engine = create_async_engine(DATABASE_URL, pool_pre_ping=True)

    try:
        for attempt in range(1, 31):
            try:
                async with engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))

                print("Database connection established.")
                return

            except Exception as exc:
                print(
                    f"Database is not ready "
                    f"(attempt {attempt}/30): {exc}"
                )
                await asyncio.sleep(2)

        raise RuntimeError("Could not connect to database after 30 attempts.")

    finally:
        await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(wait_for_db())
    except Exception as exc:
        print(f"Database startup check failed: {exc}")
        sys.exit(1)