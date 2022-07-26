import os

from pathlib import Path
from pydantic import BaseSettings, RedisDsn, PostgresDsn, Field, validator
from typing import Union
from urllib.parse import quote_plus


class AppSettings(BaseSettings):
    """
    Application settings ...
    see https://lynn-kwong.medium.com/how-to-use-pydantic-to-read-environment-variables-and-secret-files-in-python-8a6b8c56381c
    for a good tutorial on dealing with secrets and .env variables
    """

    """ Project metadata """

    project_path: Path = Path(__file__).parent.resolve()
    project_name: str = project_path.name

    """ Celery settings """

    celery_broker: RedisDsn

    @property  # use below defined RedisDSN as Celery broker.
    def celery_broker(self) -> RedisDsn:
        return self.redis_dsn

    frequency: int = 10  # default monitoring frequency
    website_url: str = "https://nf-co.re"

    """ Database settings """

    database_scheme: str = "postgresql"
    database_host: str = Field(default="nfcore_stats_db", env="DATABASE_HOST")
    database_port: int = Field(default=5432, env="DATABASE_PORT")
    database_username: str = Field(default="admin", env="POSTGRES_USER")
    database_password: str = Field(default="quest", env="POSTGRES_PASSWORD")
    database_name: str = Field(default="nf_core_stats", env="POSTGRES_DB")
    database_url: PostgresDsn
    database_salt: bytes = None
    database_pool_size: int = 3

    @property
    def database_url(self) -> PostgresDsn:
        return PostgresDsn(
            f"{self.database_scheme}://"
            f"{quote_plus(self.database_username)}:{quote_plus(self.database_password)}@"
            f"{quote_plus(self.database_host)}:{self.database_port}/"
            f"{quote_plus(self.database_name)}",
            scheme=self.database_scheme,
            host=f"{quote_plus(self.database_host)}",
        )

    """ Redis settings """

    redis_scheme: str = Field(default="redis", env="REDIS_SCHEME")
    redis_host: str = Field(default="nfcore_stats_redis", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_password: str = Field(None, env="REDIS_PASSWORD")
    redis_socket_timeout: str = None

    @property
    def redis_dsn(self) -> RedisDsn:
        return RedisDsn(
            f"{self.redis_scheme}://"
            # anonymous login to Redis (default, as direct exposure of Redis to untrusted entities is discouraged)
            f":{quote_plus(self.redis_password) if self.redis_password else ''}@"
            f"{quote_plus(self.redis_host)}:{self.redis_port}/"
            f"{self.redis_db}",
            scheme=self.redis_scheme,
            host=f"{quote_plus(self.redis_host)}",
        )

    class Config:
        """
        Meta configuration of the settings parser.
        """

        # Use a prefix for the settings
        env_prefix = ""

        @validator("database_url")
        def replace_postgres_scheme(cls, url: str) -> str:
            """
            Ensures scheme is compatible with newest version of SQLAlchemy.
            """
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            return url


class DevAppSettings(AppSettings):
    """
    Overwrite any AppSettings here or add new ones with Development specific values
    """

    debug: bool = True


class ProdAppSettings(AppSettings):
    """
    Overwrite any AppSettings here or add new ones with Production specific values
    """

    debug: bool = False


settings = dict(development=DevAppSettings, production=ProdAppSettings)

# The final app settings:
settings: Union[DevAppSettings, ProdAppSettings] = settings[
    os.environ.get("ENV", "development").lower()
]()
