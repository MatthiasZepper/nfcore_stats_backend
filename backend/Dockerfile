FROM python:3.10-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /mnt/backend
ENV PYTHONPATH /mnt/backend

COPY poetry.lock /mnt/backend/poetry.lock
COPY pyproject.toml /mnt/backend/pyproject.toml

RUN apt-get update && apt-get install -y gcc python3-dev libpq-dev
RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry show
RUN poetry install $(test "${NO_DEV}" && echo "--no-dev") --no-root

ENTRYPOINT [ "./entrypoint.sh" ]