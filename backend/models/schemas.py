from pydantic import BaseModel


class ResumeData(BaseModel):
    """Structured resume data extracted from PDF/DOCX"""

    name: str | None = None
    email: str | None = None
    phone: str | None = None
    skills: list[str] = []
    experience: list[str] = []
    education: list[str] = []
    raw_text: str


class JobDescription(BaseModel):
    """Job description input"""

    title: str
    description: str
    required_skills: list[str]
    preferred_skills: list[str] | None = []


class MatchResult(BaseModel):
    """Result of matching a resume against a job description"""

    candidate_name: str | None
    match_score: float  # 0-100
    matched_skills: list[str]
    missing_skills: list[str]
    justification: str
    qualified: bool  # True if score >= 80


class ChatMessage(BaseModel):
    """Chat message for interview"""

    role: str  # 'user' or 'assistant'
    content: str
    code_context: str | None = None


class CodeExecutionRequest(BaseModel):
    """Request to execute code"""

    code: str
    language: str = "python"


class CodeExecutionResult(BaseModel):
    """Result of code execution"""

    success: bool
    output: str
    error: str | None = None
