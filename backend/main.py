from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from routers import candidates, interview

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Recruitment System API")

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

@app.get("/")
def read_root():
    return {"message": "AI Recruitment System API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

