import http

from collections import defaultdict
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlmodel import select, SQLModel, Session

from .database_logic.db import engine, get_session
from .database_logic.pipelines_crud import PipelinesCRUD
from .database_logic.releases_crud import ReleaseCRUD
from .database_logic.remote_workflows_crud import RemoteWorkflowCRUD
from .database_logic.topics_crud import RemoteWorkflowTopicCRUD
from .models.pipelines import PipelineSummaryCreate
from .models.uptime import UptimeRecord, UptimeResponse
from .settings import settings

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
    debug=settings.debug,
    docs_url="/docs",
)


# CORS (Cross-Origin Resource Sharing)¶
# https://fastapi.tiangolo.com/tutorial/cors/
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "*"
    ],  # bind to ["http://localhost:3000"] if frontend app is served at port 3000.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create all database tables if they don't exist yet
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


@app.get("/", tags=["Status"])
async def health_check():
    return {
        "name": settings.project_name,
        "version": settings.project_version,
        "description": settings.project_description,
    }


#############################################################################################


@app.get(
    path="/get/uptime/{limit}",
    response_model=UptimeResponse,
    tags=["Uptime_Monitoring"],
)
async def get_uptime(limit: int = 10, session: Session = Depends(get_session)):
    """
    Return the last n results of the Uptime Monitoring.
    """

    try:

        statement = (
            select(UptimeRecord)
            .where(UptimeRecord.url == settings.website_url)
            .order_by(UptimeRecord.received.desc())
            .limit(limit)
        )
        result = session.exec(statement)

        response = defaultdict(list)
        for record in result:
            response[record.url].append(record)

        if settings.debug:
            print(response)

        return response

    except ValidationError:
        return http.HTTPStatus.INTERNAL_SERVER_ERROR


#############################################################################################


@app.put("/json/pipelines")
async def ingest_pipeline_info(
    *, input_data: PipelineSummaryCreate, session: Session = Depends(get_session)
):

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

    return {"OK"}
