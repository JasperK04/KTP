import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY", "supersecretkey")


config: dict[str, type[Config]] = {
    "development": Config,
    "production": Config,
}
