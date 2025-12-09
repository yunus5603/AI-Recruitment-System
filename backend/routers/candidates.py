from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from models.schemas import ResumeData, JobDescription, MatchResult
from services.resume_parser import parse_resume
from services.matcher import match_resume_to_job
import os
import tempfile
from typing import List
from sqlmodel import Session, select
from models.db import get_session, Candidate, JobMatch

router = APIRouter(prefix="/candidates", tags=["candidates"])

@router.post("/upload-resume", response_model=ResumeData)
async def upload_resume(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """
    Upload and parse a resume PDF.
    Returns structured resume data and saves to DB.
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
        
        # Save to DB
        candidate = Candidate(
            name=resume_data.name,
            email=resume_data.email,
            phone=resume_data.phone,
            skills=resume_data.skills, # Property setter handles JSON conversion
            experience=resume_data.experience,
            education=resume_data.education,
            raw_text=resume_data.raw_text,
            filename=file.filename
        )
        session.add(candidate)
        session.commit()
        session.refresh(candidate)
        
        return resume_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Clean up temp file
        if os.path.exists(tmp_file_path):
            os.unlink(tmp_file_path)

@router.post("/match", response_model=List[MatchResult])
async def match_candidates(
    job: JobDescription,
    session: Session = Depends(get_session)
):
    """
    Match all uploaded candidates against a job description.
    Returns a list of match results, sorted by score (highest first).
    Only includes candidates with score >= 80%.
    """
    candidates = session.exec(select(Candidate)).all()
    
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates uploaded yet")
    
    results = []
    
    for candidate in candidates:
        # Convert DB model back to Schema for matcher
        resume = ResumeData(
            name=candidate.name,
            email=candidate.email,
            phone=candidate.phone,
            skills=candidate.skills,
            experience=candidate.experience,
            education=candidate.education,
            raw_text=candidate.raw_text
        )
        
        match_result = await match_resume_to_job(resume, job)
        
        # Only include qualified candidates (>= 80%)
        if match_result.qualified:
            results.append(match_result)
        
        # Save match history
        job_match = JobMatch(
            candidate_id=candidate.id,
            job_title=job.title,
            match_score=match_result.match_score,
            qualified=match_result.qualified
        )
        session.add(job_match)
    session.commit()
    
    # Sort by match score (descending)
    results.sort(key=lambda x: x.match_score, reverse=True)
    
    return results

@router.get("/all", response_model=List[ResumeData])
async def get_all_candidates(session: Session = Depends(get_session)):
    """Get all uploaded candidates"""
    candidates = session.exec(select(Candidate)).all()
    return [
        ResumeData(
            name=c.name,
            email=c.email,
            phone=c.phone,
            skills=c.skills,
            experience=c.experience,
            education=c.education,
            raw_text=c.raw_text
        ) for c in candidates
    ]

@router.delete("/clear")
async def clear_candidates(session: Session = Depends(get_session)):
    """Clear all candidates from database"""
    session.exec(select(Candidate)).delete() # This might need iteration or specific delete call depending on SQLModel version
    # Safer way for SQLModel basic usage:
    candidates = session.exec(select(Candidate)).all()
    for c in candidates:
        session.delete(c)
    session.commit()
    return {"message": "All candidates cleared"}
