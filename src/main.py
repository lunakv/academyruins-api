import logging
import os
import uuid
from typing import Any, Callable

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.openapi import strings
from src.openapi.openapi_decorators import (
    ApiLogoDecorator,
    BaseResolver,
    CachingDecorator,
    Remove422Decorator,
    TagGroupsDecorator,
    ValidationErrorSchemaDecorator,
)

from .resources import seeder
from .routers import (
    admin,
    diff,
    glossary_deprecated,
    link,
    metadata,
    mtr,
    pending,
    rawfile,
    rule,
    rule_deprecated,
    unofficial_glossary_deprecated,
)
from .utils.logger import logger
from .utils.scheduler import Scheduler

logging.basicConfig(format="%(asctime)s:%(levelname)s:%(name)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

app = FastAPI(
    title=strings.title,
    version="0.4.0",
    description=strings.description,
    openapi_tags=strings.tag_dicts,
    license_info=strings.license_info,
    contact=strings.contact_info,
    redoc_url="/docs",
    docs_url="/swagger",
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(admin.router, prefix="/admin")
app.include_router(rule.router, prefix="/cr", tags=["CR"])
app.include_router(mtr.router, prefix="/mtr", tags=["MTR"])
app.include_router(link.router, prefix="/link", tags=["Redirects"])
app.include_router(diff.router, prefix="/diff", tags=["Diffs"])
app.include_router(rawfile.router, prefix="/file", tags=["Files"])
app.include_router(metadata.router, prefix="/metadata")
app.include_router(pending.router, prefix="/pending")
# --- DEPRECATED ROUTERS --- #
app.include_router(rule_deprecated.router, deprecated=True, tags=["Deprecated"])
app.include_router(glossary_deprecated.router, prefix="/glossary", deprecated=True, tags=["Deprecated"])
app.include_router(
    unofficial_glossary_deprecated.router, prefix="/unofficial-glossary", deprecated=True, tags=["Deprecated"]
)
# -------------------------- #

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
async def seed():
    await seeder.seed()


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
