import uuid
from datetime import date, datetime, timedelta

from pydantic import HttpUrl, UUID4, validator
from sqlmodel import Field, Relationship, SQLModel
from typing import Dict, List, Optional

from .github_user import GithubUser

"""
Each model entity in this file may have several associated models declared:

    ModelEntityBASE: This is a data model only that specifies the core attributes of an entity
    ModelEntity: Inherits from BASE and is the actual table model (table=True) including relationships.
    ModelEntityCREATE: The values required to create an Instance of the model entity. 
    ModelEntityREAD: The values returned as response if a particular model entity is read, may be multiple for different applications.
    ModelEntityModelEntityLINK: Association tables for Many-to-Many relationships.

    See https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/ for the benefits of this approach.  
"""


class PullRequestStatsBase(SQLModel):
    """
    The PullRequestStatsBase model is the main model for an statistical aggregate across all PRs in nf-core for a given time point.
    """

    count: int = Field(
        ..., description="The total count of issues across the organization."
    )
    open_count: int = Field(
        ..., description="The total count of open issues across the organization."
    )
    comments_count: int = Field(
        ..., description="The number of comments for all repos."
    )
    authors_count: int = Field(..., description="The headcount of authors involved.")
    median_close_time: timedelta = Field(
        ..., description="The median time for an issue to be open."
    )
    median_response_time: timedelta = Field(
        ..., description="The median time before someone replied to an open issue."
    )


class PullRequestStats(PullRequestStatsBase, table=True):
    """
    The PullRequestStats model table
    """

    received: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the aggregation was performed.",
        primary_key=True,
    )


class PullRequestBase(SQLModel):
    """
    The IssueBase model to gather all issues from all repos.
    """

    url: HttpUrl = Field(..., description="URL of the issue on Github")
    comments_url: HttpUrl = (
        Field(..., description="API URL of the issue's comments."),
    )
    html_url: HttpUrl = (
        Field(..., description="URL of the issue's comments on Github"),
    )
    state: str = Field(..., description="state of the issue")
    num_comments: int = (
        Field(..., description="How many comments are recorded for the issue"),
    )
    created_at: datetime = (Field(..., description="Creation date of the issue"),)
    updated_at: datetime = (Field(..., description="Update date of the issue"),)
    closed_at: Optional[datetime] = (
        Field(..., description="Closing date of the issue, if exists"),
    )
    closed_wait: Optional[timedelta] = (
        Field(..., description="Creation date of the issue"),
    )
    first_reply: datetime = (Field(..., description="When did somebody reply?"),)
    first_reply_wait: timedelta = (
        Field(..., description="How long did the issue remain unanswered?"),
    )

    @validator("url", "comments_url", "html_url", pre=True)
    def replace_backslashes(cls, v):
        """
        Replace backslash escapes in URLs. See validator of ReleaseBase for a more detailed info.
        """
        return v.replace("\\", "")


class PullRequest(PullRequestBase, table=True):
    """
    The PullRequest table model
    """

    __tablename__ = "pullrequests"
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)

    repo: str = Field(..., description="The repo the PR is associated with")
    running_number: int = Field(..., description="The running number of the PR.")

    # One to many relationship: One user can have created many issues and PRs, but each is linked to one GithubUser only.
    # Unfortunately, we need to link GithubUsers twice (the creator and the first reply)
    # In regular SQLAlchemy that would be easily solved with relationship(foreign_keys="...")
    # (https://docs.sqlalchemy.org/en/14/orm/join_conditions.html#handling-multiple-join-paths)
    # SQLModel Relationship however doesn't support this respectively fails to create connections when sa_relationship_kwargs are used with foreign_keyes.
    # Finally solved with https://github.com/tiangolo/sqlmodel/issues/10

    created_by_id: UUID4 = Field(default=None, foreign_key="githubuser.id")
    created_by: GithubUser = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PullRequest.created_by_id]"}
    )

    first_reply_by_id: UUID4 = Field(default=None, foreign_key="githubuser.id")
    first_reply_by: GithubUser = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[PullRequest.first_reply_by_id]"}
    )


class PullRequestCreate(PullRequestBase):
    repo: Optional[str]
    running_number: Optional[int]
    created_by: str
    first_reply_by: str


class PullRequestsArrayCreate(SQLModel):
    """
    Weird single aggregated item within "stats" in nfcore_issue_stats.json. Only two items divert from the regular schema StatsIssuePullRequestAggregateCreate in .models.issues
    """

    daily_opened: Dict[date, int]
    daily_closed: Dict[date, int]
    close_times: List[int]
    response_times: List[int]


PullRequest.update_forward_refs()