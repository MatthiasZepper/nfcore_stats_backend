from sqlmodel import create_engine, SQLModel

from .settings import settings

engine = create_engine(
    settings.database_url, pool_size=settings.database_pool_size, pool_pre_ping=True
)
