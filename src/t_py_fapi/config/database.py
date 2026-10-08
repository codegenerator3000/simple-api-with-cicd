from sqlalchemy.engine import URL
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    host: str = "db"
    port: int = 3306
    name: str
    user: str
    password: str


settings = DatabaseSettings()

database_url = URL.create(
    "mysql+asyncmy",
    username=settings.user,
    password=settings.password,
    host=settings.host,
    port=settings.port,
    database=settings.name,
)
