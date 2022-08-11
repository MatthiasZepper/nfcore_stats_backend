from fastapi import HTTPException
from fastapi import status as http_status
from pydantic import AnyUrl
from sqlmodel import delete, select, Session
from typing import Union

from ..models.pipelines import RemoteWorkflow, RemoteWorkflowBase, RemoteWorkflowCreate


class RemoteWorkflowCRUD:
    """
    The RemoteWorkflow model holds a list of workflows on Github, each having tags and releases.
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: RemoteWorkflowCreate) -> RemoteWorkflow:
        # Weird issue: When building the function like PipelinesCRUD.create, I got the error:
        # *** AttributeError: 'dict' object has no attribute '_sa_instance_state'
        # After a lot of failed attempts, I figured out by trial and error, that running it again through RemoteWorkflowCreate in combination with .from_orm()
        # worked. Sadly poorly documented in https://sqlmodel.tiangolo.com/tutorial/fastapi/multiple-models/#use-multiple-models-to-create-a-hero
        rmc = RemoteWorkflowCreate(**data) 
        remote_workflow = RemoteWorkflow.from_orm(rmc)
        self.session.add(remote_workflow)
        self.session.commit()
        self.session.refresh(remote_workflow)

        return remote_workflow

    def get(self, remote_workflow_id: int, raise_exc: bool = True) -> RemoteWorkflow:

        statement = select(RemoteWorkflow).where(
            RemoteWorkflow.id == remote_workflow_id
        )
        results = self.session.execute(statement=statement)
        remote_workflow = results.scalar_one_or_none()

        # optional to fail silently and return None if
        if remote_workflow is None and raise_exc:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="This remote workflow hasn't been found!",
            )

        return remote_workflow

    def exists(
        self, query: RemoteWorkflowBase, raise_exc: bool = True
    ) -> RemoteWorkflow:

        if hasattr(query,"git_url"): #gitURL is probably safer than name to check for duplicates

            statement = select(RemoteWorkflow).where(RemoteWorkflow.git_url == query.git_url)

        elif hasattr(query,"name"):

            statement = select(RemoteWorkflow).where(RemoteWorkflow.name == query)
        
        else:
            return None  #no possibility to check for duplication.

        results = self.session.execute(statement=statement)
        remote_workflow = results.scalar_one_or_none()

        # optional to fail silently and return None if
        if remote_workflow is None and raise_exc:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="This remote workflow hasn't been found!",
            )

        return remote_workflow

    def patch(
        self, remote_workflow_id: int, data: RemoteWorkflowCreate
    ) -> RemoteWorkflow:

        remote_workflow = self.get(
            remote_workflow_id=remote_workflow_id, raise_exc=True
        )
        values = data.dict(exclude_unset=True)

        for k, v in values.items():
            if hasattr(remote_workflow, k):
                setattr(remote_workflow, k, v)

        self.session.add(remote_workflow)
        self.session.commit()
        self.session.refresh(remote_workflow)

        return remote_workflow

    def delete(self, remote_workflow_id: int) -> bool:

        statement = delete(RemoteWorkflow).where(
            RemoteWorkflow.id == remote_workflow_id
        )

        self.session.execute(statement=statement)
        self.session.commit()

        return (
            True  # deleting a non-existing value is valid SQL, so return always true.
        )
