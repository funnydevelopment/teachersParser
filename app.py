import asyncio
import datetime

from dotenv import load_dotenv

from core import services


async def run_app():
    load_dotenv(".env")
    print(f"Скрипт начал работать в {datetime.datetime.now()}")
    await services.get_len_json_data()


if __name__ == "__main__":
    asyncio.run(run_app())
