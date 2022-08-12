import http

from collections import defaultdict
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlmodel import select, SQLModel, Session

from .database_logic.db import engine, get_session
from .database_logic.pipelines_crud import PipelinesCRUD
from .database_logic.remote_workflows_crud import RemoteWorkflowCRUD
from .models.pipelines import (
    PipelineSummaryCreate,
    PipelineSummary,
    PipelineSummaryBase,
    RemoteWorkflowCreate,
    RemoteWorkflowTopicCreate,
)
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
    crud = PipelinesCRUD(session=session)

    # check if pipeline_summary has already been imported
    # since its ID is unknown, match the value of updated
    pipeline_summary = crud.exists(query=input_data, raise_exc=False)

    if not pipeline_summary:
        pipeline_summary = crud.create(data=input_data)
    else:
        pipeline_summary = crud.patch(
            pipeline_summary_id=pipeline_summary.id, data=input_data
        )

    # create and link the remote workflows.
    crud = RemoteWorkflowCRUD(session=session)

    for input_workflow in input_data.remote_workflows:
        
        remote_workflow = crud.exists(query=input_workflow, raise_exc=False)
        
        if not remote_workflow:
            remote_workflow = crud.create(data=input_workflow)
        else:
            remote_workflow = crud.patch(
                remote_workflow_id=remote_workflow.id, data=input_workflow
            )
        
        for release in input_workflow.releases:
            print(release)

        for topic in input_workflow.topics:
            pass

        import pdb; pdb.set_trace()

    return {"OK"}
