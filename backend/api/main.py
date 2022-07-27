import http
import json

from collections import defaultdict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlmodel import select, SQLModel, Session

from .db import engine
from .models import UptimeRecord, UptimeResponse
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
SQLModel.metadata.create_all(engine)


@app.get(path="/uptime/{limit}", response_model=UptimeResponse, tags=["Uptime_Monitoring"])
async def get_uptime(limit: int = 10):
    """
    Return the last n results of the Uptime Monitoring.
    """

    try:

        with Session(engine) as session:
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

            return(response)

    except ValidationError:
        return http.HTTPStatus.INTERNAL_SERVER_ERROR
