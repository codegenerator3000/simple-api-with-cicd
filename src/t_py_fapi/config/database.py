from sqlalchemy.engine import URL
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(
            env_prefix="DB_",
            env_file=".env",
            extra="ignore",
            )

    host: str
    port: int
    name: str
    user: str
    password: SecretStr


settings = DatabaseSettings()

database_url = URL.create(
    "mysql+asyncmy",
    username=settings.user,
    password=settings.password.get_secret_value(),
    host=settings.host,
    port=settings.port,
    database=settings.name,
)
