import asyncio

from dotenv import load_dotenv

from core import services


async def run_app():
    load_dotenv(".env")
    #await services.get_schools_urls()
    await services.get_teachers_urls()


if __name__ == "__main__":
    asyncio.run(run_app())
