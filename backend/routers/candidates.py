from fastapi import APIRouter, UploadFile, File, HTTPException
from models.schemas import ResumeData, JobDescription, MatchResult
from services.resume_parser import parse_resume
from services.matcher import match_resume_to_job
import os
import tempfile
from typing import List

router = APIRouter(prefix="/candidates", tags=["candidates"])

# In-memory storage for demo purposes
candidates_db: List[dict] = []

@router.post("/upload-resume", response_model=ResumeData)
async def upload_resume(file: UploadFile = File(...)):
    """
    Upload and parse a resume PDF.
    Returns structured resume data.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_file_path = tmp_file.name
    
    try:
        # Parse the resume
        resume_data = await parse_resume(tmp_file_path)
        
        # Store in our in-memory database
        candidates_db.append({
            "resume": resume_data.model_dump(),
            "filename": file.filename
        })
        
        return resume_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

@router.post("/match", response_model=List[MatchResult])
async def match_candidates(job: JobDescription):
    """
    Match all uploaded candidates against a job description.
    Returns a list of match results, sorted by score (highest first).
    Only includes candidates with score >= 80%.
    """
    if not candidates_db:
        raise HTTPException(status_code=400, detail="No candidates uploaded yet")
    
    results = []
    
    for candidate in candidates_db:
        resume = ResumeData(**candidate["resume"])
        match_result = await match_resume_to_job(resume, job)
        
        # Only include qualified candidates (>= 80%)
        if match_result.qualified:
            results.append(match_result)
    
    # Sort by match score (descending)
    results.sort(key=lambda x: x.match_score, reverse=True)
    
    return results

@router.get("/all", response_model=List[ResumeData])
async def get_all_candidates():
    """Get all uploaded candidates"""
    return [ResumeData(**c["resume"]) for c in candidates_db]

@router.delete("/clear")
async def clear_candidates():
    """Clear all candidates from memory"""
    candidates_db.clear()
    return {"message": "All candidates cleared"}
