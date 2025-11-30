from pydantic import BaseModel
from typing import List, Optional

class ResumeData(BaseModel):
    """Structured resume data extracted from PDF/DOCX"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    skills: List[str] = []
    experience: List[str] = []
    education: List[str] = []
    raw_text: str

class JobDescription(BaseModel):
    """Job description input"""
    title: str
    description: str
    required_skills: List[str]
    preferred_skills: Optional[List[str]] = []

class MatchResult(BaseModel):
    """Result of matching a resume against a job description"""
    candidate_name: Optional[str]
    match_score: float  # 0-100
    matched_skills: List[str]
    missing_skills: List[str]
    justification: str
    qualified: bool  # True if score >= 80

class ChatMessage(BaseModel):
    """Chat message for interview"""
    role: str  # 'user' or 'assistant'
    content: str

class CodeExecutionRequest(BaseModel):
    """Request to execute code"""
    code: str
    language: str = "python"

class CodeExecutionResult(BaseModel):
    """Result of code execution"""
    success: bool
    output: str
    error: Optional[str] = None
