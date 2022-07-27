from datetime import datetime

from pydantic import HttpUrl
from sqlmodel import Field, SQLModel
from typing import List, Optional, Union


class Release(SQLModel):
    """
    The Release model stores the pipeline release information
    """

    name: str
    published_at: str
    html_url: str
    tag_name: str
    tag_sha: str
    draft: bool
    prerelease: bool
    tarball_url: str
    zipball_url: str


class RemoteWorkflow(SQLModel):
    """
    The RemoteWorkflow model is the main model representing the information for each pipeline.
    """

    id: int
    name: str
    full_name: str
    private: bool
    html_url: str
    description: Optional[str]
    topics: List[str]
    created_at: str
    updated_at: str
    pushed_at: str
    last_release: Union[int, str]
    git_url: str
    ssh_url: str
    clone_url: str
    size: int
    stargazers_count: int
    forks_count: int
    archived: bool
    releases: List[Release]


class Pipelines(SQLModel):
    """
    The Pipelines model is the top-level model that enriches a list of RemoteWorkflows with some metadata.
    """

    updated: int
    pipeline_count: int
    published_count: int
    devel_count: int
    archived_count: int
    remote_workflows: List[RemoteWorkflow]
