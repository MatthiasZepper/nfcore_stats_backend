import re
import uuid
from datetime import datetime

from pydantic import HttpUrl, UUID4, validator
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional

"""
Each model entity in this file may have several associated models declared:

    ModelEntityBASE: This is a data model only that specifies the core attributes of an entity
    ModelEntity: Inherits from BASE and is the actual table model (table=True) including relationships.
    ModelEntityCREATE: The values required to create an Instance of the model entity. 
    ModelEntityREAD: The values returned as response if a particular model entity is read, may be multiple for different applications.
    ModelEntityModelEntityLINK: Association tables for Many-to-Many relationships.

    See https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/ for the benefits of this approach.  
"""


class GithubUserBase(SQLModel):

    username: str = Field(..., description="Github user name")
    profile_url: HttpUrl = Field(
        ..., description="The URL to get to the user's page on Github."
    )
    profile_img_url: HttpUrl = Field(
        ..., description="The URL of the profile picture of the user."
    )

    @validator("profile_url", "profile_img_url", pre=True)
    def replace_backslashes(cls, v):
        """
        Replace backslash escapes in URLs. See validator of ReleaseBase for a more detailed info.
        """
        return v.replace("\\", "")


class GithubUser(GithubUserBase, table=True):
    __tablename__ = "githubuser"
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)

    # specifying a formal Relationship with back_populates here will cause sqlalchemy.exc.AmbiguousForeignKeysError for Issue and PullRequest,
    # because they reference GithubUser twice (for created_by and first_reply_by Relationships). If a table has only a single relationship
    # putting Relationship(back_populates="...") works perfectly, see RemoteWorkflow and Release.
    # Also mind that SQLModels Relationship and SQLAlchemy.ORM's relationship() have slightly different args, e.g. one needs the foreign_keys to be specified as
    # ["foreign_key"] and the other one as "[foreign_key]".
    # Something I learned the hard way and wasted many more hours on ORM peculiarities (How about switching to MongoDB? Anyone?).

    # Anyway: Github Users are referenced as foreign.id at:
    # Issue.created_by (table: issues.created_by_id)
    # Issue.first_reply_by (table: issues.first_reply_by_id)
    # PullRequest.created_by (table: pullrequests.created_by_id)
    # PullRequest.first_reply_by (table: pullrequests.first_reply_by_id)


# The create models for nfcore_issue_stats.json import


class AuthorIssueStatsCreate(SQLModel):
    num_created: int
    num_replies: int
    num_first_response: int


class AuthorPullRequestStatsCreate(SQLModel):
    num_created: int
    num_replies: int
    num_first_response: int


class AuthorStatsCreate(SQLModel):
    prs: Optional[AuthorPullRequestStatsCreate]
    issues: Optional[AuthorIssueStatsCreate]
    first_contribution: Optional[datetime]
