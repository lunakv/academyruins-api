import logging

import uvicorn
from fastapi import FastAPI, Response, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from starlette.responses import StreamingResponse

from .resources import seeder
from .utils.scheduler import Scheduler
from .utils.responses import StatusResponse
from .routers import admin, glossary, link, rule

load_dotenv()
logging.basicConfig(
    format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
    datefmt='%Y-%m-%d %H:%M:%S')
app = FastAPI(default_response_class=StatusResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)
seeder.seed()

app.include_router(admin.router, prefix='/admin')
app.include_router(glossary.router, prefix='/glossary')
app.include_router(link.router, prefix='/link')
app.include_router(rule.router)

Scheduler().start()


@app.get("/", include_in_schema=False, status_code=400)
def root():
    return {
        'details': 'This is the root of the Academy Ruins API. You can find the documentation at '
                   'https://api.academyruins.com/docs'}
