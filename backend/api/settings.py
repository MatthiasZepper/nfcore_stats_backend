from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    Application settings ...
    """

    debug: bool = False
    celery_broker: str = "redis://nfcore_stats_redis:6379/0"
    frequency: int = 1  # default monitoring frequency
    database_url: str = "postgresql://admin:quest@nfcore_stats_db:8812/qdb"
    database_pool_size: int = 3
    website_url: str = "https://nf-co.re"

    class Config:
        """
        Meta configuration of the settings parser.
        """

        # Prefix the environment variable not to mix up with other variables
        # used by the OS or other software.
        env_prefix = "nfcore_"


settings = Settings()
