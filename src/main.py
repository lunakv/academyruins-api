import logging
import os
import uuid
from typing import Any, Callable

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.admin.router import router as admin_router
from src.cr.router import router as cr_router
from src.diffs.router import router as diff_router
from src.ipg.router import router as ipg_router
from src.link.router import router as link_router
from src.mtr.router import router as mtr_router
from src.openapi import strings
from src.openapi.openapi_decorators import (
    ApiLogoDecorator,
    BaseResolver,
    CachingDecorator,
    Remove422Decorator,
    TagGroupsDecorator,
    ValidationErrorSchemaDecorator,
)
from src.resources import seeder
from src.utils.logger import logger
from src.utils.scheduler import Scheduler

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

app = FastAPI(
    title=strings.title,
    version="0.7.0",
    description=strings.description,
    openapi_tags=strings.tag_dicts,
    license_info=strings.license_info,
    contact=strings.contact_info,
    redoc_url="/docs",
    docs_url="/swagger",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(admin_router)
app.include_router(cr_router)
app.include_router(mtr_router)
app.include_router(ipg_router)
app.include_router(link_router)
app.include_router(diff_router)

Scheduler().start()


def compose_api_resolver() -> Callable[[], dict[str, Any]]:
    resolver = BaseResolver(app.openapi)
    resolver = Remove422Decorator(app.routes, resolver)
    resolver = ValidationErrorSchemaDecorator(resolver)
    resolver = TagGroupsDecorator(strings.tag_groups, resolver)
    if os.environ.get("ENV") == "production":
        # logos are hosted statically on develop
        resolver = ApiLogoDecorator("https://academyruins.com/title-dark.png", "Academy Ruins logo", resolver)
    return CachingDecorator(app, resolver).get_schema


app.openapi = compose_api_resolver()


@app.on_event("startup")
def seed():
    seeder.seed()


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    return JSONResponse({"detail": str(exc)}, status_code=422)


@app.exception_handler(500)
def internal_error_handler(request, exc):
    error_id = str(uuid.uuid4())
    logger.error(f"Error ID {error_id}")
    try:
        detail = str(exc)
    except Exception:
        detail = "Internal Server Error"

    return JSONResponse({"detail": detail, "error_id": error_id}, status_code=500)


@app.get("/", include_in_schema=False, status_code=400)
def root():
    return {
        "detail": "This is the root of the Academy Ruins API. You can find the documentation at "
        "https://api.academyruins.com/docs"
    }
