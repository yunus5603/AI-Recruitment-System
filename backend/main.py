import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()  # before importing modules that read settings at import time

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from models.db import create_db_and_tables  # noqa: E402
from routers import analytics, candidates, interview  # noqa: E402
from services import llm  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(title="AI Recruitment System API", version="1.0.0", lifespan=lifespan)

origins = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(candidates.router)
app.include_router(interview.router)
app.include_router(analytics.router)


@app.get("/")
def read_root():
    return {"message": "AI Recruitment System API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy", "demo_mode": llm.demo_mode()}
