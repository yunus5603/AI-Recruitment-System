import json
import os
import tempfile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session, delete, select

from models.db import Candidate, JobMatch, get_session
from models.schemas import JobDescription, MatchResult, ResumeData
from services.matcher import match_resume_to_job
from services.resume_parser import parse_resume

router = APIRouter(prefix="/candidates", tags=["candidates"])

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_MB", "5")) * 1024 * 1024


def to_resume(candidate: Candidate) -> ResumeData:
    return ResumeData(
        name=candidate.name,
        email=candidate.email,
        phone=candidate.phone,
        skills=candidate.skills,
        experience=candidate.experience,
        education=candidate.education,
        raw_text=candidate.raw_text,
    )


@router.post("/upload-resume", response_model=ResumeData)
async def upload_resume(file: UploadFile = File(...), session: Session = Depends(get_session)):
    """Upload a resume PDF, parse it into structured data and store it."""
    if not (file.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File is too large")
    if not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="File is not a valid PDF")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        resume_data = await parse_resume(tmp_file_path)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Resume parsing failed: {e}") from e
    finally:
        os.unlink(tmp_file_path)

    session.add(
        Candidate(
            name=resume_data.name,
            email=resume_data.email,
            phone=resume_data.phone,
            skills_json=json.dumps(resume_data.skills),
            experience_json=json.dumps(resume_data.experience),
            education_json=json.dumps(resume_data.education),
            raw_text=resume_data.raw_text,
            filename=file.filename,
        )
    )
    session.commit()
    return resume_data


@router.post("/match", response_model=list[MatchResult])
async def match_candidates(job: JobDescription, session: Session = Depends(get_session)):
    """Score every stored candidate against a job description.

    Every score is saved for analytics. Only qualified candidates (score >= 80)
    are returned, highest score first.
    """
    candidates = session.exec(select(Candidate)).all()
    if not candidates:
        raise HTTPException(status_code=400, detail="No candidates uploaded yet")

    results = []
    for candidate in candidates:
        try:
            match = await match_resume_to_job(to_resume(candidate), job)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Matching failed: {e}") from e

        session.add(
            JobMatch(
                candidate_id=candidate.id,
                job_title=job.title,
                match_score=match.match_score,
                qualified=match.qualified,
            )
        )
        if match.qualified:
            results.append(match)
    session.commit()

    results.sort(key=lambda r: r.match_score, reverse=True)
    return results


@router.get("/all", response_model=list[ResumeData])
async def get_all_candidates(session: Session = Depends(get_session)):
    """Get all uploaded candidates"""
    return [to_resume(c) for c in session.exec(select(Candidate)).all()]


@router.delete("/clear")
async def clear_candidates(session: Session = Depends(get_session)):
    """Delete all candidates and their match history"""
    session.exec(delete(JobMatch))
    session.exec(delete(Candidate))
    session.commit()
    return {"message": "All candidates cleared"}
