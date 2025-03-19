# Code by AkinoAlice@TyrantRey

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from application import authorization, history, report, result, search

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
    prefix="/api/v1",
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
