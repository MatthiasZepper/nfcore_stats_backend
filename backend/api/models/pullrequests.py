import re
import uuid
from datetime import datetime

from pydantic import AnyUrl, HttpUrl, UUID4, timedelta, validator
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional, Set, Union

"""
Each model entity in this file may have several associated models declared:

    ModelEntityBASE: This is a data model only that specifies the core attributes of an entity
    ModelEntity: Inherits from BASE and is the actual table model (table=True) including relationships.
    ModelEntityCREATE: The values required to create an Instance of the model entity. 
    ModelEntityREAD: The values returned as response if a particular model entity is read, may be multiple for different applications.
    ModelEntityModelEntityLINK: Association tables for Many-to-Many relationships.

    See https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/ for the benefits of this approach.  
"""


class PullRequestsStatsBase(SQLModel):
    """
    The PullRequestStatsBase model is the main model for an statistical aggregate across all PRs in nf-core for a given time point.
    """

    count: int = Field(..., description="The total count of issues across the organization.")
    open_count: int = Field(..., description="The total count of open issues across the organization.")
    comments_count: int = Field(..., description="The number of comments for all repos.")
    authors_count: int = Field(..., description="The headcount of authors involved.")
    median_close_time: timedelta = Field(..., description="The median time for an issue to be open.")
    median_response_time: timedelta = Field(..., description="The median time before someone replied to an open issue.")


class PullRequestsStats(PullRequestsStatsBase, table=True):
    """
    The PullRequestStats model table
    """
    
    received: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the aggregation was performed.",
        primary_key=True,
    )
