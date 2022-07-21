FROM python:3.8-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /mnt/backend

RUN apt-get update && apt-get install -y gcc python3-dev libpq-dev
RUN pip install poetry

RUN poetry config virtualenvs.create false && poetry install $(test "${NO_DEV}" && echo "--no-dev") --no-root

ENV PYTHONPATH /mnt/backend

ENTRYPOINT [ "./entrypoint.sh" ]