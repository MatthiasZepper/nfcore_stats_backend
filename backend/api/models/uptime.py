from datetime import datetime

from pydantic import HttpUrl
from sqlmodel import Field, SQLModel
from typing import Dict, List, Union


class UptimeRecord(SQLModel, table=True):
    """
    The UptimeRecord model stores, if a website or HTTP service was available at a given time.
    """

    url: Union[HttpUrl, None] = Field(..., description="The monitored URL")
    http_status: int = Field(..., description="HTTP status code returned by upstream")
    available: bool = Field(..., description="Represents the service availability")
    received: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the signal received",
        primary_key=True,
    )


class UptimeResponse(SQLModel, table=False):
    """
    API response model for UptimeRecord (table=False, because it is only used as Pydantic BaseModel)

    Finally, this works after 8h thanks to https://stackoverflow.com/a/69329476
    https://pydantic-docs.helpmanual.io/usage/models/#custom-root-types
    """

    __root__: Dict[HttpUrl, List[Union[UptimeRecord, None]]]
