from fastapi import APIRouter, Depends
from pydantic import ValidationError
from sqlmodel import Session

from ..database_logic.db import get_session
from ..database_logic.pipelines_crud import PipelinesCRUD
from ..database_logic.releases_crud import ReleaseCRUD
from ..database_logic.remote_workflows_crud import RemoteWorkflowCRUD
from ..database_logic.topics_crud import RemoteWorkflowTopicCRUD
from ..models.issues import IssueStatsAggregateCreate
from ..models.pipelines import PipelineSummaryCreate

router = APIRouter(
    prefix="/import",
    tags=["json", "import", "backup"],
    # dependencies=[Depends(get_token_header)], #for authentication later
    responses={404: {"description": "Not found"}},
)


@router.put("/pipelines")
async def ingest_pipeline_info(
    *, input_data: PipelineSummaryCreate, session: Session = Depends(get_session)
):
    """
    Import function for pipelines.json
    """

    # initiate database operation -> easy transition to async CRUD later if needed.
    # SQLModel's versions of select and delete might be async by default...hhm.
    p_crud = PipelinesCRUD(session=session)

    # check if pipeline_summary has already been imported
    # since its ID is unknown, match the value of updated
    pipeline_summary = p_crud.exists(query=input_data, raise_exc=False)

    if not pipeline_summary:
        pipeline_summary = p_crud.create(data=input_data)
    else:
        pipeline_summary = p_crud.patch(
            pipeline_summary_id=pipeline_summary.id, data=input_data
        )

    # create and link the remote workflows.
    rw_crud = RemoteWorkflowCRUD(session=session)

    for input_workflow in input_data.remote_workflows:

        remote_workflow = rw_crud.exists(query=input_workflow, raise_exc=False)

        if not remote_workflow:
            remote_workflow = rw_crud.create(data=input_workflow)
        else:
            remote_workflow = rw_crud.patch(
                remote_workflow_id=remote_workflow.id, data=input_workflow
            )

        # create and link the releases.
        r_crud = ReleaseCRUD(session=session)

        for input_release in input_workflow["releases"]:

            release = r_crud.exists(query=input_release, raise_exc=False)

            # link release to it's remote workflow
            remote_workflow = rw_crud.exists(query=input_workflow, raise_exc=False)
            if remote_workflow and hasattr(remote_workflow, "id"):
                input_release["remote_workflow_id"] = remote_workflow.id

            if not release:
                release = r_crud.create(data=input_release)
            else:
                release = r_crud.patch(
                    workflow_release_sha=release.tag_sha, data=input_release
                )

        # create and link the topics.
        t_crud = RemoteWorkflowTopicCRUD(session=session)

        for input_topic in input_workflow["topics"]:

            topic = t_crud.exists(query=input_topic, raise_exc=False)

            if not topic:
                topic = t_crud.create(data=input_topic)
            else:
                topic = t_crud.patch(topic_id=topic.id, data=input_topic)

            # async, therefore a session.refresh is necessary.
            # Nonetheless I get seemingly random
            # sqlalchemy.orm.exc.UnmappedInstanceError: Class 'builtins.NoneType' is not mapped
            # errors for some records, therefore these weird nested if clauses.

            # session.refresh() didn't help...switching to exists function.

            remote_workflow = rw_crud.exists(query=input_workflow, raise_exc=False)
            topic = t_crud.exists(query=input_topic, raise_exc=False)

            if remote_workflow and topic:
                remote_workflow.topics = [topic]
                session.add(remote_workflow)
                session.commit()

    # async, therefore a session.refresh is necessary.
    # Nonetheless I get seemingly random
    # sqlalchemy.orm.exc.UnmappedInstanceError: Class 'builtins.NoneType' is not mapped
    # errors for some records, therefore these weird nested if clauses.

    for input_workflow in input_data.remote_workflows:

        pipeline_summary = p_crud.exists(query=input_data, raise_exc=False)
        remote_workflow = rw_crud.exists(query=input_workflow, raise_exc=False)

        if pipeline_summary and remote_workflow:
            pipeline_summary.remote_workflow.append(remote_workflow)

        session.add(pipeline_summary)
        session.commit()

    return {"Import of pipelines.json successful"}


@router.put("/issue_stats")
async def ingest_issue_stats_info(
    *, input_data: IssueStatsAggregateCreate, session: Session = Depends(get_session)
):
    """
    Import function for nfcore_issue_stats.json
    """
    import pdb

    pdb.set_trace()
    return {"Import of nfcore_issue_stats.json successful"}
