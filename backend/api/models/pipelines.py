import uuid
from datetime import datetime

from pydantic import AnyUrl, BaseModel, Json,  HttpUrl, UUID4, validator
from sqlmodel import Field, SQLModel
from typing import List, Optional


class Release(SQLModel, table=True):
    """
    The Release model stores the pipeline release information
    """
    name: str = Field(..., description="The release version, sometimes including a release code name.")
    published_at: datetime = Field(..., description="The time point when the release was created.")
    html_url: HttpUrl = Field(..., description="The URL for the release.")
    tag_name: str = Field(..., description="The tag associated with the release")
    tag_sha: str = Field(default=None, primary_key=True, description="The sha256 checksum for the release.")
    draft: bool = Field(..., description="If the respective release is a draft oder regular release.")
    prerelease: bool = Field(..., description="If the release in question is marked as prerelease.")
    tarball_url: HttpUrl = Field(..., description="The URL to download the .tar archive of the released pipeline.")
    zipball_url: HttpUrl = Field(..., description="Where to download the .zip archive of the release.")

    @validator('html_url', 'tarball_url', 'zipball_url', pre=True)
    def replace_backslashes(cls, v):
        """
        In order to make the URl fields validate, we need to replace the backslashes before:
        https:\/\/api.github.com\/repos\/nf-core\/ampliseq\/tarball\/1.0.0

        This function is therefore not a validator, but a convenient place to put the string replace.
        """
        return v.replace("\\", "")

class RemoteWorkflowTopics(SQLModel, table=True):
    """
    A separate class/database table to handle tags efficiently.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    topics: str = Field(..., description="Topics that can be associated with a pipeline.")

class RemoteWorkflow(SQLModel, table=True):
    """
    The RemoteWorkflow model is the main model representing the information for each pipeline.
    """

    id: int = Field(default=None, primary_key=True, description="The ID of the remote workflow.")
    name: str = Field(..., description="The base name of the pipeline/repo.")
    full_name: Field(..., description="The full name of the pipeline/repo including nf-core.")
    private: bool = Field(..., description="Is the repository private or publicly visible?")
    html_url: HttpUrl = Field(..., description="The URL of the repository on Github.")
    description: Optional[str]  = Field(..., description=" The description of the repository.")
    topics: Optional[List[RemoteWorkflowTopics]] 
    created_at: datetime  = Field(..., description="The time point when the workflow was created.")
    updated_at: datetime  = Field(..., description="The last time this workflow was updated.")
    pushed_at: datetime  = Field(..., description="The most recent push to this workflow.")
    last_release: Optional[datetime]  = Field(..., description="The date of the last release, if any.")
    git_url: AnyUrl  = Field(..., description="The git URL of the repository.")
    ssh_url: str  = Field(..., description="The ssh URI")
    clone_url: HttpUrl  = Field(..., description="The URL to clone the repo from.")
    size: int  = Field(..., description="The size of the repository.")
    stargazers_count: int  = Field(..., description="How many people have starred the repository.")
    forks_count: int  = Field(..., description="How many public forks of a repository exist?")
    archived: bool  = Field(..., description="Is the workflow current or archived?")
    releases: List[Release]

    @validator('html_url', 'git_url', 'clone_url', pre=True)
    def replace_backslashes(cls, v):
        """
        Replace backslash escapes in URLs as before. Reusing the validator was impossible due to execution order.
        """
        return v.replace("\\", "")


class Pipelines(SQLModel, table=True):
    """
    The Pipelines model is the top-level model that enriches a list of RemoteWorkflows with some metadata.
    """
    id: UUID4 = Field(default_factory=uuid.uuid4, primary_key=True)
    received: Optional[datetime] = Field(default_factory=datetime.utcnow, description="Timestamp when the JSON information was received.")
    updated: int = Field(..., description="The update count of the JSON.")
    pipeline_count: int = Field(..., description="The number of pipelines in nf-core.")
    published_count: int = Field(..., description="The number of published pipelines in nf-core.")
    devel_count: int = Field(..., description="How many pipelines are currently under development.")
    archived_count: int = Field(..., description="The size of the pipeline archive.")
    remote_workflows: List[RemoteWorkflow]


class PipelinesLoadAPI(BaseModel, table=False):
    """
    The PipelinesLoad model is used in API endpoint for importing a pipelines.json to the database.
    """
    json_obj: Json[Pipelines]
