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
        values = data.dict()
        remote_workflow = RemoteWorkflow(**values)
        self.session.add(remote_workflow)
        self.session.commit()
        self.session.refresh(remote_workflow)

        return remote_workflow

    def get(self, remote_workflow_id: int, raise_exc: bool = True) -> RemoteWorkflow:

        statement = select(RemoteWorkflow).where(
            RemoteWorkflow.id == remote_workflow_id
        )
        results = self.session.execute(statement=statement)
        remote_workflow = results.scalar_one_or_none(inherit_cache=True)

        # optional to fail silently and return None if
        if remote_workflow is None and raise_exc:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="This remote workflow hasn't been found!",
            )

        return remote_workflow

    def get_by_name_or_github(
        self, query: Union[str, AnyUrl], raise_exc: bool = True
    ) -> RemoteWorkflow:

        if isinstance(query, AnyUrl):

            statement = select(RemoteWorkflow).where(RemoteWorkflow.git_url == query)

        else:

            statement = select(RemoteWorkflow).where(RemoteWorkflow.name == query)

        results = self.session.execute(statement=statement)
        remote_workflow = results.scalar_one_or_none(inherit_cache=True)

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
