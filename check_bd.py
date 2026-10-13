
import asyncio

from sqlalchemy import text
from app.database import engine


async def main():
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT 1"))
        value = result.scalar_one()

        print(f"Подключение успешно! Результат: {value}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
