from fastapi import HTTPException
from fastapi import status as http_status
from sqlmodel import delete, select, Session

from ..models.pipelines import RemoteWorkflowTopic, RemoteWorkflowTopicBase, RemoteWorkflowTopicCreate


class RemoteWorkflowTopicCRUD:
    """
    The RemoteWorkflowTopic model holds a list of topics that the workflows are associated with.
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: RemoteWorkflowTopicCreate) -> RemoteWorkflowTopic:

        if isinstance(data, dict):
            topic = RemoteWorkflowTopic.parse_obj(data)
        else: #likely str then
            topic = RemoteWorkflowTopic.parse_obj({"topic" : data})

        self.session.add(topic)
        self.session.commit()
        self.session.refresh(topic)

        return topic

    def get(self, topic_id: int, raise_exc: bool = True) -> RemoteWorkflowTopic:
        """
        Function to select a RemoteWorkflowTopic by it's ID.
        """

        statement = select(RemoteWorkflowTopic).where(
            RemoteWorkflowTopic.id == topic_id
        )
        results = self.session.execute(statement=statement)
        topic = results.scalar_one_or_none()

        # optional to fail silently and return None
        if topic is None and raise_exc:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="This remote workflow hasn't been found!",
            )

        return topic

    def exists(
        self, query: RemoteWorkflowTopicCreate, raise_exc: bool = True
    ) -> RemoteWorkflowTopic:
        """
        Function to check if a RemoteWorkflowTopic already exists in database. (Without knowing the ID)
        """

        # .ilike() is a SQLAlchemy way of caseinsensitive comparison. 
        statement = select(RemoteWorkflowTopic).where(RemoteWorkflowTopic.topic.ilike(query))
        results = self.session.execute(statement=statement)
        topic = results.scalar_one_or_none()

        # optional to fail silently and return None if
        if topic is None and raise_exc:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="This remote workflow hasn't been found!",
            )

        return topic

    def patch(
        self, topic_id: int, data: RemoteWorkflowTopicBase
    ) -> RemoteWorkflowTopic:

        topic = self.get(
            topic_id=topic_id, raise_exc=True
        )

        if isinstance(data, dict):
            values = RemoteWorkflowTopicBase(**data).dict()
        else: #likely str then
            values = {"topic" : data}

        for k, v in values.items():
            if hasattr(topic, k):
                setattr(topic, k, v)

        self.session.add(topic)
        self.session.commit()
        self.session.refresh(topic)

        return topic

    def delete(self, topic_id: int) -> bool:

        statement = delete(RemoteWorkflowTopic).where(
            RemoteWorkflowTopic.id == topic_id
        )

        self.session.execute(statement=statement)
        self.session.commit()

        return (
            True  # deleting a non-existing value is valid SQL, so return always true.
        )
