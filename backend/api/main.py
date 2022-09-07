from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from .database_logic.db import engine
from .routers import import_json, uptime
from .settings import settings

app = FastAPI(
    title=settings.project_name,
    description=settings.project_description,
    version=settings.project_version,
    debug=settings.debug,
    docs_url="/docs",
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


@app.get("/", tags=["Status"])
async def health_check():
    return {
        "name": settings.project_name,
        "version": settings.project_version,
        "description": settings.project_description,
    }


# see https://fastapi.tiangolo.com/tutorial/bigger-applications/ for alternative ways of configuring the routers.
app.include_router(import_json.router)  # the endpoints to import data into the database
app.include_router(uptime.router)  # the endpoints to monitor uptime
