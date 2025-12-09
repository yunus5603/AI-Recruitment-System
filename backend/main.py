from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from routers import candidates, interview, analytics

# Load environment variables
load_dotenv()

from contextlib import asynccontextmanager
from models.db import create_db_and_tables

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="AI Recruitment System API", lifespan=lifespan)

# Configure CORS
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(candidates.router)
app.include_router(interview.router)
app.include_router(analytics.router)

@app.get("/")
def read_root():
    return {"message": "AI Recruitment System API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

