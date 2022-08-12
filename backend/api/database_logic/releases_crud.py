from fastapi import HTTPException
from fastapi import status as http_status
from sqlmodel import delete, select, Session

from ..models.pipelines import Release, ReleaseBase, ReleaseCreate


class ReleaseCRUD:
    """
    The Release model stores the information associated with a particular pipeline release on Github.
    It is a sub-item of the RemoteWorkflows.
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: ReleaseCreate) -> Release:
        rc = ReleaseCreate(**data) 
        workflow_release = Release.from_orm(rc)
        self.session.add(workflow_release)
        self.session.commit()
        self.session.refresh(workflow_release)

        return workflow_release

    def get(self, workflow_release_sha: str, raise_exc: bool = True) -> Release:
        """
        Function to select a Release by it's ID - the sha
        """

        statement = select(Release).where(
            Release.tag_sha == workflow_release_sha
        )
        results = self.session.execute(statement=statement)
        workflow_release = results.scalar_one_or_none()

        # optional to fail silently and return None if
        if workflow_release is None and raise_exc:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="This remote workflow hasn't been found!",
            )

        return workflow_release

    def exists(
        self, query: ReleaseCreate, raise_exc: bool = True
    ) -> Release:
        """
        Function to check if a Release already exists in database.
        (Actually not relevant, since database uses sha as key, so it is always known)
        """

        rc = ReleaseCreate(**query) 
        query = Release.from_orm(rc)

        if hasattr(query,"tag_sha"): # use tag_sha as prime method of checking identity.

            statement = select(Release).where(Release.tag_sha == query.tag_sha)

        elif hasattr(query,"tag_name"):

            statement = select(Release).where(Release.tag_name == query.tag_name)
        
        else:
            return None  #no possibility to check for duplication.

        results = self.session.execute(statement=statement)
        workflow_release = results.scalar_one_or_none()

        # optional to fail silently and return None if
        if workflow_release is None and raise_exc:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="This remote workflow hasn't been found!",
            )

        return workflow_release

    def patch(
        self, workflow_release_sha: str, data: ReleaseBase
    ) -> Release:

        workflow_release = self.get(
            workflow_release_sha=workflow_release_sha, raise_exc=True
        )

        # filter the nested levels (releases and tags), otherwise patching fails.
        values = ReleaseBase(**data).dict()

        for k, v in values.items():
            if hasattr(workflow_release, k):
                setattr(workflow_release, k, v)

        self.session.add(workflow_release)
        self.session.commit()
        self.session.refresh(workflow_release)

        return workflow_release

    def delete(self, workflow_release_sha: str) -> bool:

        statement = delete(Release).where(
            Release.tag_sha == workflow_release_sha
        )

        self.session.execute(statement=statement)
        self.session.commit()

        return (
            True  # deleting a non-existing value is valid SQL, so return always true.
        )
