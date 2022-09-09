import re
import uuid
from datetime import date, datetime, timedelta

from pydantic import HttpUrl, UUID4, validator
from sqlmodel import Field, Relationship, SQLModel
from typing import Dict, List, Optional, Union


from .github_user import GithubUser, AuthorStatsCreate
from .pullrequests import PullRequestStatsBase, PullRequestsArrayCreate, PullRequestCreate

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

class IssueStatsCreate(IssueStatsBase):
    """
    The IssueStats Create schema
    """
    received: datetime


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
    first_reply: datetime = Field(..., description="When did somebody reply?"),
    first_reply_wait: timedelta = Field(..., description="How long did the issue remain unanswered?"),
    talking_to_myself: Optional[int] = Field(..., description="No idea what that value is...?!?"),

    @validator("url", "comments_url", "html_url", pre=True)
    def replace_backslashes(cls, v):
        """
        Replace backslash escapes in URLs. See validator of ReleaseBase for a more detailed info.
        """
        return v.replace("\\", "")

class Issue(IssueBase, table=True):
    """
    The Issue table model
    """
    __tablename__ = "issues"
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)

    repo: str = Field(..., description="The repo the issue is associated with")
    running_number: int = Field(..., description="The running number of the issue.")

    # One to many relationship: One user can have created many issues and PRs, but each is linked to one GithubUser only.
    # Unfortunately, we need to link GithubUsers twice (the creator and the first reply)
    # In regular SQLAlchemy that would be easily solved with relationship(foreign_keys="...")
    # (https://docs.sqlalchemy.org/en/14/orm/join_conditions.html#handling-multiple-join-paths)
    # SQLModel Relationship however doesn't support this respectively fails to create connections when sa_relationship_kwargs are used with foreign_keyes.
    # Finally solved with https://github.com/tiangolo/sqlmodel/issues/10

    created_by_id: UUID4 = Field(default=None, foreign_key="githubuser.id")
    created_by: GithubUser = Relationship(sa_relationship_kwargs={"primaryjoin": "issues.created_by_id==githubuser.id", "lazy": "joined"})

    first_reply_by_id: UUID4 = Field(default=None, foreign_key="githubuser.id")
    first_reply_by: GithubUser = Relationship(sa_relationship_kwargs={"primaryjoin": "issues.first_reply_by_id==githubuser.id", "lazy": "joined"})

class IssueCreate(IssueBase):
    repo: Optional[str]
    running_number: Optional[int]
    created_by: str
    first_reply_by: str 


class RepoCreate(SQLModel):
    """
    For each repo, a all issues and PRs are listed,  items of the "repo" dict in nfcore_issue_stats.json
    """
    issues: Optional[Dict[int,IssueCreate]]
    prs: Optional[Dict[int,PullRequestCreate]]

class StatsIssuePullRequestAggregateCreate(SQLModel):
    """
    Daily aggregates of the issues and PRs, items of the "stats" dict in nfcore_issue_stats.json
    """
    issues: IssueStatsBase
    prs: PullRequestStatsBase


class IssuesArrayCreate(SQLModel):
    """
    Weird single aggregated item within "stats" in nfcore_issue_stats.json. Only two items divert from the regular schema StatsIssuePullRequestAggregateCreate.
    """
    daily_opened: Dict[date,int]
    daily_closed: Dict[date,int]
    close_times: List[int]
    response_times: List[int]


class IssueStatsAggregateCreate(SQLModel):
    """
    The top-level Create Validation Schema for the nfcore_issues_stats.json import
    """
    updated: datetime
    stats: Union[StatsIssuePullRequestAggregateCreate,IssuesArrayCreate,PullRequestsArrayCreate] #daily stats aggregates plus two orphaned arrays weirdly intermixed there.
    repos: Dict[str,RepoCreate]
    authors: Dict[str,AuthorStatsCreate]



Issue.update_forward_refs()