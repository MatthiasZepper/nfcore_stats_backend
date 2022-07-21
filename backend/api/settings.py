import os

from pathlib import Path
from pydantic import (
    BaseSettings,
    RedisDsn,
    PostgresDsn,
    Field,
    validator
)
from typing import Union

class AppSettings(BaseSettings):
    """
    Application settings ...
    see https://lynn-kwong.medium.com/how-to-use-pydantic-to-read-environment-variables-and-secret-files-in-python-8a6b8c56381c
    for a good tutorial on dealing with secrets and .env variables
    """

    project_path: Path = Path(__file__).parent.resolve()
    project_name: str = PROJECT_PATH.name

    celery_broker: RedisDsn = Field(default='redis://nfcore_stats_redis:6379/0', env='REDIS_URL')
    frequency: int = 1  # default monitoring frequency
    database_url: PostgresDsn = Field(default='postgresql://admin:quest@nfcore_stats_db:8812/qdb', env='DATABASE_URL')
    database_pool_size: int = 3
    website_url: str = "https://nf-co.re"

    class Config:
        """
        Meta configuration of the settings parser.
        """
        # Use a prefix for the settings.
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


settings = dict(
    development=DevAppSettings,
    production=ProdAppSettings
)

# The final app settings:
settings: Union[DevAppSettings, ProdAppSettings] = settings[os.environ.get('ENV', 'development').lower()]()
