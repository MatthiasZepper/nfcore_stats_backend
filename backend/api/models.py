from datetime import datetime

from sqlmodel import Field, SQLModel
from typing import List


class UptimeMonitor(SQLModel, table=True):
    """
    The UptimeMonitor model can be used to see if a website or HTTP service is available at a given time.
    """

    url: str = Field(..., description="The monitored URL")
    http_status: int = Field(..., description="HTTP status code returned by upstream")
    available: bool = Field(..., description="Represents the service availability")
    received: datetime = Field(
        ..., description="Timestamp when the signal received", primary_key=True
    )


class UptimeResponse(SQLModel, table=False):
    """
    API response model for UptimeMonitor (table=False, because it is only used as Pydantic BaseModel)
    """

    url: str
    records: List[UptimeMonitor]
