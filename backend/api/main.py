import http

from collections import defaultdict
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlmodel import select, SQLModel, Session

from .db import engine, get_session
from .models.pipelines import PipelineSummary, RemoteWorkflow, RemoteWorkflowTopic
from .models.uptime import UptimeRecord, UptimeResponse
from .settings import settings

app = FastAPI(
    title="nf-core stats API",
    description="This service collects and returns the statistics for the nf-core community.",
    version="0.1.0",
    debug=settings.debug,
    docs_url=None,
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
    pipeline_summary: PipelineSummary, session: Session = Depends(get_session)
):

    statement = select(PipelineSummary).where(
        PipelineSummary.updated == pipeline_summary.updated
    )
    existing_pipeline_summary = session.exec(statement).first()

    if (
        existing_pipeline_summary
    ):  # this file has already been imported to the database.

        print(item for item in pipeline_summary.remote_workflow)
        return {"This version of pipeline.json has already been imported."}

    else:  # this version of pipelines.json was not imported yet.
        session.add(pipeline_summary)
        session.commit()
        session.refresh(pipeline_summary)

        if pipeline_summary.remote_workflow:  # there are associated workflows
            for remote_workflow in pipeline_summary.remote_workflow:

                statement = select(RemoteWorkflow).where(
                    RemoteWorkflow.name == remote_workflow.name
                )
                existing_remote_workflow = session.exec(statement)

                if existing_remote_workflow:
                    remote_workflow_data = remote_workflow.dict(exclude_unset=True)
                    for key, value in remote_workflow_data.items():
                        setattr(existing_remote_workflow, key, value)
                        session.add(existing_remote_workflow)
                        session.commit()
                        session.refresh(existing_remote_workflow)

                else:
                    session.add(remote_workflow)
                    session.commit(remote_workflow)
                    session.refresh(remote_workflow)

        return {"OK"}
