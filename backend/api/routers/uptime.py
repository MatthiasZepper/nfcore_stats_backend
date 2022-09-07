import http

from collections import defaultdict
from fastapi import APIRouter, Depends
from pydantic import ValidationError
from sqlmodel import select, Session

from ..database_logic.db import get_session
from ..models.uptime import UptimeRecord, UptimeResponse
from ..settings import settings


router = APIRouter(
    prefix="/uptime",
    tags=["uptime", "service", "watcher"],
    # dependencies=[Depends(get_token_header)], #for authentication later
    responses={404: {"description": "Not found"}},
)


@router.get(
    path="/{limit}",
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
