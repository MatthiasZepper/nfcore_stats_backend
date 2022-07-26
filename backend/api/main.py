import http

from collections import defaultdict
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select, SQLModel, Session
from typing import List

from .db import engine
from .models import UptimeMonitor, UptimeResponse
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


@app.get(path="/uptime", response_model=UptimeResponse, tags=["Uptime_Monitoring"])
async def get_uptime(limit: int = 10):
    """
    Return the stored uptime monitoring results.

    The returned signals will be sorted by `received` timestamp in a decreasing
    order, limited to `10` records if `limit` not set.
    """

    try:

        with Session(engine) as session:
            statement = (
                select(UptimeMonitor)
                .where(UptimeMonitor.url == settings.website_url)
                .order_by(UptimeMonitor.received)
                .limit(limit)
            )
            result = session.exec(statement)

            response = defaultdict(list)
            for record in result:
                response[record.url].append(record)

            print(response)

            return [
                UptimeResponse(url=url, records=records)
                for url, records in response.items()
            ]
    except:
        return http.HTTPStatus.INTERNAL_SERVER_ERROR
