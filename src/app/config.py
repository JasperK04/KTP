import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    QUESTIONS_FILE_PATH = os.environ.get("QUESTIONS_FILE_PATH", "questions.json")
    RULES_FILE_PATH = os.environ.get("RULES_FILE_PATH", "rules.json")


config: dict[str, type[Config]] = {
    "development": Config,
    "production": Config,
}
