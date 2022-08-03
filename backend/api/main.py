import http

from collections import defaultdict
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlmodel import select, SQLModel, Session

from .db import engine, get_session
from .models.pipelines import PipelinesLoadAPI, PipelineSummary
from .models.uptime import UptimeRecord, UptimeResponse
from .settings import settings

app = FastAPI(
    title="nf-core stats API",
    description="This service collects and returns the statistics for the nf-core community.",
    version="0.1.0",
    debug=settings.debug,
    docs_url=None,
)

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
    json_obj: PipelineSummary, session: Session = Depends(get_session)
):
    session.add(json_obj)
    session.commit()
    session.refresh(json_obj)
    return {"OK"}
