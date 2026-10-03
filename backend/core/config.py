import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Meowhere API"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://meow_user:meow_password@localhost:5432/meowhere_db"
    )

    class Config:
        env_file = ".env"

settings = Settings()