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


class IssueStatsBase(SQLModel):
    """
    The IssueStatsBase model is the main model for an statistical aggregate across all issues in nf-core for a given time point.
    """

    count: int = Field(..., description="The total count of issues across the organization.")
    open_count: int = Field(..., description="The total count of open issues across the organization.")
    comments_count: int = Field(..., description="The number of comments for all repos.")
    authors_count: int = Field(..., description="The headcount of authors involved.")
    median_close_time: timedelta = Field(..., description="The median time for an issue to be open.")
    median_response_time: timedelta = Field(..., description="The median time before someone replied to an open issue.")

class IssueStats(IssueStatsBase, table=True):
    """
    The IssueStats model table
    """
    
    received: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the aggregation was performed",
        primary_key=True,
    )


class IssueBase(SQLModel):
    """
    The IssueBase model to gather all issues from all repos.
    """
    url: HttpUrl = Field(..., description="URL of the issue on Github")
    comments_url: HttpUrl = Field(..., description="API URL of the issue's comments."),
    html_url: HttpUrl = Field(..., description="URL of the issue's comments on Github"),
    state: str = Field(..., description="state of the issue")
    num_comments: int = Field(..., description="How many comments are recorded for the issue"),
    created_at: datetime = Field(..., description="Creation date of the issue"),
    updated_at: datetime = Field(..., description="Update date of the issue"),
    closed_at: Optional[datetime] = Field(..., description="Closing date of the issue, if exists"),
    closed_wait: Optional[timedelta] = Field(..., description="Creation date of the issue"),
    created_by: str = Field(..., description="Creator of the issue"),
    first_reply: datetime = Field(..., description="When did somebody reply?"),
    first_reply_wait: timedelta = Field(..., description="How long did the issue remain unanswered?"),
    first_reply_by: str = Field(..., description="Who replied first?")

    @validator("url", "comments_url", "html_url", pre=True)
    def replace_backslashes(cls, v):
        """
        Replace backslash escapes in URLs. See validator of ReleaseBase for a more detailed info.
        """
        return v.replace("\\", "")

