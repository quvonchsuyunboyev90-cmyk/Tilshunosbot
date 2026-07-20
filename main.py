import asyncio

from aiogram import Bot, Dispatcher

from config import TELEGRAM_TOKEN


bot = Bot(token=TELEGRAM_TOKEN)

dp = Dispatcher()


async def main():
    print("AI Football Analyst v1.0 ishga tushdi")


if __name__ == "__main__":
    asyncio.run(main())
