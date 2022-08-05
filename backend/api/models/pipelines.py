import uuid
from datetime import datetime

from pydantic import AnyUrl, BaseModel, Json, HttpUrl, UUID4, validator
from sqlmodel import Field, Relationship, SQLModel
from typing import List, Optional, Set

"""
Each model entity in this file may have several associated models declared:

    ModelEntityBASE: This is a data model only that specifies the core attributes of an entity
    ModelEntity: Inherits from BASE and is the actual table model (table=True) including relationships.
    ModelEntityCREATE: The values required to create an Instance of the model entity. 
    ModelEntityREAD: The values returned as response if a particular model entity is read, may be multiple for different applications.
    ModelEntityModelEntityLINK: Association tables for Many-to-Many relationships.

    See https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/ for the benefits of this approach.  
"""


#### The association tables
class RemoteWorkflowTopicLink(SQLModel, table=True):
    """
    The RemoteWorkflowTopicLink is link table between RemoteWorkflow and RemoteWorkflowTopic.
    """

    remote_workflow_id: Optional[int] = Field(
        default=None, foreign_key="remoteworkflow.id", primary_key=True
    )
    topic_id: Optional[int] = Field(
        default=None, foreign_key="remoteworkflowtopic.id", primary_key=True
    )


class RemoteWorkflowPipelineSummaryLink(SQLModel, table=True):
    """
    The RemoteWorkflowPipelineSummaryLink is link table between RemoteWorkflow and PipelineSummary.
    """

    remote_workflow_id: Optional[int] = Field(
        default=None, foreign_key="remoteworkflow.id", primary_key=True
    )
    pipeline_summary_id: Optional[UUID4] = Field(
        default=None, foreign_key="pipelinesummary.id", primary_key=True
    )


#### Remote Workflow - aka Pipelines - Models


class RemoteWorkflowBase(SQLModel):
    """
    The RemoteWorkflow model is the main model representing the information for each pipeline.
    """

    id: int = Field(
        default=None, primary_key=True, description="The ID of the remote workflow."
    )
    name: str = Field(..., description="The base name of the pipeline/repo.")
    full_name: str = Field(
        ..., description="The full name of the pipeline/repo including nf-core."
    )
    private: bool = Field(
        ..., description="Is the repository private or publicly visible?"
    )
    html_url: HttpUrl = Field(..., description="The URL of the repository on Github.")
    description: Optional[str] = Field(
        ..., description=" The description of the repository."
    )

    created_at: datetime = Field(
        ..., description="The time point when the workflow was created."
    )
    updated_at: datetime = Field(
        ..., description="The last time this workflow was updated."
    )
    pushed_at: datetime = Field(
        ..., description="The most recent push to this workflow."
    )
    last_release: Optional[datetime] = Field(
        ..., description="The date of the last release, if any."
    )
    git_url: AnyUrl = Field(..., description="The git URL of the repository.")
    ssh_url: str = Field(..., description="The ssh URI")
    clone_url: HttpUrl = Field(..., description="The URL to clone the repo from.")
    size: int = Field(..., description="The size of the repository.")
    stargazers_count: int = Field(
        ..., description="How many people have starred the repository."
    )
    forks_count: int = Field(
        ..., description="How many public forks of a repository exist?"
    )
    archived: bool = Field(..., description="Is the workflow current or archived?")

    @validator("html_url", "git_url", "clone_url", pre=True)
    def replace_backslashes(cls, v):
        """
        Replace backslash escapes in URLs. See validator of ReleaseBase for a more detailed info.
        """
        return v.replace("\\", "")


class RemoteWorkflow(RemoteWorkflowBase, table=True):  # the table model

    # Using "Release" and "PipelineSummary" in quotes because we haven't declared that class yet by this point in the code (but SQLModel understands that).
    # We however later need to update_forward_refs(), such that from_orm() will work.
    topics: Optional[Set["RemoteWorkflowTopic"]] = Relationship(
        back_populates="remote_workflows", link_model=RemoteWorkflowTopicLink
    )
    releases: Optional[List["Release"]] = Relationship(back_populates="remote_workflow")
    pipeline: Optional[List["PipelineSummary"]] = Relationship(
        back_populates="remote_workflow", link_model=RemoteWorkflowPipelineSummaryLink
    )

    class Config:
        orm_mode = True


class RemoteWorkflowCreate(RemoteWorkflowBase):
    topics: Optional[Set["RemoteWorkflowTopic"]]
    releases: Optional[List["Release"]]
    pipeline: Optional[List["PipelineSummary"]]


#### Release - Models


class ReleaseBase(SQLModel):
    """
    The Release model stores the pipeline release information
    """

    name: str = Field(
        ..., description="The release version, sometimes including a release code name."
    )
    published_at: datetime = Field(
        ..., description="The time point when the release was created."
    )
    html_url: HttpUrl = Field(..., description="The URL for the release.")
    tag_name: str = Field(..., description="The tag associated with the release")
    tag_sha: str = Field(
        default=None,
        primary_key=True,
        description="The sha256 checksum for the release.",
    )
    draft: bool = Field(
        ..., description="If the respective release is a draft oder regular release."
    )
    prerelease: bool = Field(
        ..., description="If the release in question is marked as prerelease."
    )
    tarball_url: HttpUrl = Field(
        ...,
        description="The URL to download the .tar archive of the released pipeline.",
    )
    zipball_url: HttpUrl = Field(
        ..., description="Where to download the .zip archive of the release."
    )

    # One to many relationship: One remote workflow can have many releases, but each release is linked to one workflow only.
    remote_workflow_id: int = Field(default=None, foreign_key="remoteworkflow.id")

    @validator("html_url", "tarball_url", "zipball_url", pre=True)
    def replace_backslashes(cls, v):
        """
        In order to make the URl fields validate, we need to replace the backslashes before:
        https:\/\/api.github.com\/repos\/nf-core\/ampliseq\/tarball\/1.0.0

        This function is therefore not a validator, but a convenient place to put the string replace.
        """
        return v.replace("\\", "")


class Release(ReleaseBase, table=True):
    remote_workflow: RemoteWorkflow = Relationship(back_populates="releases")


#### RemoteWorkflow Topics - aka Tags - Models


class RemoteWorkflowTopicBase(SQLModel):
    """
    A separate class/database table to handle tags efficiently.
    """

    topic: str = Field(
        ..., description="Topics that can be associated with a pipeline."
    )


class RemoteWorkflowTopic(RemoteWorkflowTopicBase, table=True):
    """
    A separate class/database table to handle tags efficiently.
    """

    id: Optional[int] = Field(default=None, primary_key=True)

    # many to many relationship with remote workflows.
    remote_workflows: List[RemoteWorkflow] = Relationship(
        back_populates="topics", link_model=RemoteWorkflowTopicLink
    )

    class Config:
        orm_mode = True


class RemoteWorkflowTopicCreate(SQLModel):

    pass


#### The Pipeline Summary Model: Meta-model for ingesting data


class PipelineSummaryBase(SQLModel):
    """
    The PipelineSummary model is the top-level model that enriches a list of RemoteWorkflows with some metadata.
    """

    received: Optional[datetime] = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when the JSON information was received.",
    )
    updated: int = Field(..., description="The update count of the JSON.")
    pipeline_count: int = Field(..., description="The number of pipelines in nf-core.")
    published_count: int = Field(
        ..., description="The number of published pipelines in nf-core."
    )
    devel_count: int = Field(
        ..., description="How many pipelines are currently under development."
    )
    archived_count: int = Field(..., description="The size of the pipeline archive.")


class PipelineSummary(PipelineSummaryBase, table=True):

    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)

    # One to many relationship: Each Pipeline summary can reference a remote workflow only once.
    remote_workflow: Optional[Set["RemoteWorkflow"]] = Relationship(
        back_populates="pipeline", link_model=RemoteWorkflowPipelineSummaryLink
    )

    class Config:
        orm_mode = True


class PipelineSummaryCreate(PipelineSummaryBase):
    """
    The PipelineSummaryCreate model is used in API endpoint for importing a pipelines.json file into the database.
    """

    remote_workflows: List


# Update the forward refs to make the Relationships work in main.py with .from_orm()

RemoteWorkflow.update_forward_refs()
RemoteWorkflowTopic.update_forward_refs()
PipelineSummary.update_forward_refs()
