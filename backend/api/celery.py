"""
Celery Beat, the built-in periodic task scheduler implementation of Celery is used for the periodic scrapes.
Import Celery for creating tasks, and crontab for constructing Unix-like crontabs.
"""


from celery import Celery
from celery.schedules import crontab

from .main import settings

celery_app = Celery("tasks", broker=settings.celery_broker)
celery_app.autodiscover_tasks()

MONITORING_TASK = 'api.tasks.monitor'

celery_app.conf.task_routes = {MONITORING_TASK: "main-queue"}

# Schedule the monitoring task
celery_app.conf.beat_schedule = {
    "monitor": {
        "task": MONITORING_TASK,
        "schedule": crontab(
            minute=f"*/{settings.frequency}"  # Run the task every X minutes
        ),
    }
}
