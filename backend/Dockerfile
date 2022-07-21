FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /mnt/backend
ENV PYTHONPATH /mnt/backend

# required for Poetry to find the files for some reason even though the whole dir is mounted
COPY poetry.lock /mnt/backend/poetry.lock
COPY pyproject.toml /mnt/backend/pyproject.toml

RUN apt-get update && apt-get install -y gcc python3-dev libpq-dev uvicorn celery
RUN pip install poetry

RUN poetry show
RUN poetry config virtualenvs.create false && poetry install $(test "${NO_DEV}" && echo "--no-dev") --no-root

ENTRYPOINT [ "./entrypoint.sh" ]