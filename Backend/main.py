# Code by AkinoAlice@TyrantRey

import os
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from Backend.application import history, report, result
from Backend.application.auth import authorization
from Backend.application.search import search

app = FastAPI()
# development
if os.getenv("DEBUG") is None:
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
    prefix="/api/v1/authorization",
    tags=["Authorization", "v1"],
)
app.include_router(
    search.router,
    prefix="/api/v1",
    tags=["Search", "v1"],
)
app.include_router(
    result.router,
    prefix="/api/v1",
    tags=["Result", "v1"],
)
app.include_router(
    history.router,
    prefix="/api/v1",
    tags=["History", "v1"],
)
app.include_router(
    report.router,
    prefix="/api/v1",
    tags=["Report", "v1"],
)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
