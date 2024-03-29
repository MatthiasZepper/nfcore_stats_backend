from fastapi import HTTPException
from fastapi import status as http_status
from pydantic import UUID4
from sqlmodel import delete, select, Session
from typing import Union

from ..models.pipelines import (
    PipelineSummary,
    PipelineSummaryBase,
    PipelineSummaryCreate,
)


class PipelinesCRUD:
    """
    The PipelineSummary model is the top-level model that enriches a list of RemoteWorkflows with some metadata.
    """

    def __init__(self, session: Session):
        self.session = session

    def create(self, data: PipelineSummaryCreate) -> PipelineSummary:
        if isinstance(data, dict):
            values = data
        else:
            values = data.dict()

        pipeline_summary = PipelineSummary(**values)
        self.session.add(pipeline_summary)
        self.session.commit()
        self.session.refresh(pipeline_summary)

        return pipeline_summary

    def get(
        self, pipeline_summary_id: Union[UUID4, str], raise_exc: bool = True
    ) -> PipelineSummary:

        statement = select(PipelineSummary).where(
            PipelineSummary.id == pipeline_summary_id
        )
        results = self.session.execute(statement=statement)
        pipeline_summary = results.scalar_one_or_none()

        # optional to fail silently and return None if
        if pipeline_summary is None and raise_exc:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="This pipeline summary hasn't been found!",
            )

        return pipeline_summary

    def exists(
        self, query: PipelineSummaryBase, raise_exc: bool = True
    ) -> PipelineSummary:

        if hasattr(
            query, "updated"
        ):  # gitURL is probably safer than name to check for duplicates

            statement = select(PipelineSummary).where(
                PipelineSummary.updated == query.updated
            )

        else:
            return None  # no possibility to check for duplication.

        results = self.session.execute(statement=statement)
        pipeline_summary = results.scalar_one_or_none()

        # optional to fail silently and return None if
        if pipeline_summary is None and raise_exc:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="This pipeline summary hasn't been found!",
            )

        return pipeline_summary

    def patch(
        self, pipeline_summary_id: Union[UUID4, str], data: PipelineSummaryCreate
    ) -> PipelineSummary:

        pipeline_summary = self.get(
            pipeline_summary_id=pipeline_summary_id, raise_exc=True
        )

        if isinstance(data, dict):
            values = data
        else:
            values = data.dict()

        for k, v in values.items():
            if hasattr(pipeline_summary, k):
                setattr(pipeline_summary, k, v)

        self.session.add(pipeline_summary)
        self.session.commit()
        self.session.refresh(pipeline_summary)

        return pipeline_summary

    def delete(self, pipeline_summary_id: Union[UUID4, str]) -> bool:

        statement = delete(PipelineSummary).where(
            PipelineSummary.id == pipeline_summary_id
        )

        self.session.execute(statement=statement)
        self.session.commit()

        return (
            True  # deleting a non-existing value is valid SQL, so return always true.
        )
