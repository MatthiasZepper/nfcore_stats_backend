from sqlmodel import create_engine, Session
from sqlmodel.sql.expression import Select, SelectOfScalar

# Temporary fix for bug in SQLModel 0.0.6: https://github.com/tiangolo/sqlmodel/issues/189
SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

from ..settings import settings


# check_same_thread is a configuration that SQLAlchemy passes to the low-level library in charge of communicating with the database.
# We need to disable it because in FastAPI each request could be handled by multiple interacting threads.
# However, we will make sure we don't share the same session in more than one request, thus preventing those problems
# that warrant the default setting of "check_same_thread" as being True.
# connect_args = {"check_same_thread": False}
# connect_args["echo"]=True if settings.debug else False

engine = create_engine(
    settings.database_url,
    pool_size=settings.database_pool_size,
    pool_pre_ping=True,  # connect_args=connect_args
)


def get_session() -> Session:
    with Session(engine) as session:
        yield session
