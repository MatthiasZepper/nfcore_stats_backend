from datetime import datetime
from sqlmodel import Session

import requests

from .celery import celery_app
from .database_logic.db import engine
from .models.uptime import UptimeRecord
from .settings import settings


@celery_app.task
def monitor():
    """
    Send request to the monitored URL to check its availability.

    For monitoring the URL we will use HTTP HEAD requests to reduce the round
    trip time of request-response, as we don't need to retrieve the static
    resources served by the website.
    """

    try:
        response = requests.head(settings.website_url)

        status = UptimeRecord(
            url=settings.website_url,
            http_status=response.status_code,
            received=datetime.now(),
            available=response.status_code >= 200 and response.status_code < 400,
        )

    except Exception as exc:

        status = UptimeRecord(
            url=settings.website_url,
            http_status=-1,
            received=datetime.now(),
            available=False,
        )

        raise exc

    finally:
        with Session(engine) as session:
            session.add(status)
            session.commit()
