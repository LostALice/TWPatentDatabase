# Code by AkinoAlice@TyrantRey

import os
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from Backend.application.auth import authorization
from Backend.application.history import history
from Backend.application.report import report
from Backend.application.response import response
from Backend.application.search import search
from Backend.utility.handler.log_handler import Logger

app = FastAPI()

# development
GLOBAL_DEBUG_MODE = os.getenv("DEBUG")
logger = Logger().get_logger()
logger.info("Global Debug Mode: %s", GLOBAL_DEBUG_MODE)

if GLOBAL_DEBUG_MODE is None or GLOBAL_DEBUG_MODE == "True":
    from dotenv import load_dotenv

    load_dotenv("./.env")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    authorization.router,
    prefix="/api/v1",
    tags=["Authorization"],
)
app.include_router(
    search.router,
    prefix="/api/v1",
    tags=["Search"],
)
app.include_router(
    history.router,
    prefix="/api/v1",
    tags=["History"],
)
app.include_router(
    report.router,
    prefix="/api/v1",
    tags=["Report"],
)
app.include_router(
    response.router,
    prefix="/api/v1",
    tags=["Response"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response


if GLOBAL_DEBUG_MODE == "True":
    from Backend.application.dev import dev

    app.include_router(
        dev.router,
        prefix="/api/v1",
        tags=["Test"],
    )
