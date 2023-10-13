from dotenv import load_dotenv

from core import services


def run_app():
    load_dotenv(".env")
    services.index()


if __name__ == "__main__":
    run_app()
