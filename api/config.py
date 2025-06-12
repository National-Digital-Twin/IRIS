import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), os.pardir, ".env"),
        env_file_encoding="utf-8",
    )

    ENVIRONMENT: str = "DEV"
    PORT: int = 5021

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str

    JENA_URL: str = "localhost"
    JENA_PORT: int = 3030
    JENA_PROTOCOL: str = "http"
    ONTO_DATASET: str = "ontology"
    DATASET: str = "knowledge"
    DATA_URI: str = "http://ndtp.co.uk/data#"
    UPDATE_MODE: str = "SCG"
    ACCESS_PROTOCOL: str = "http"
    ACCESS_HOST: str = "localhost"
    ACCESS_PORT: int = 8091
    DEV_MODE: bool = True
    ACCESS_PATH: str = "/"
    IDENTITY_API_URL: str
    LANDING_PAGE_URL: str = "http://localhost:5173"
    BOOTSTRAP_SERVERS: str = "localhost:9092"
    IES_TOPIC: str = "knowledge"

    def get_db_connection_string(self):
        if self.ENVIRONMENT == "TEST":
            return None
        else:
            return f"postgresql+asyncpg://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:5432/iris"


@lru_cache
def get_settings():
    return Settings()
