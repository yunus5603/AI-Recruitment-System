from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from datetime import datetime
import json

# Database setup
sqlite_file_name = "recruitment.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# Models

class Candidate(SQLModel, table=True):
    """Database model for candidates"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    # Storage as JSON strings for simplicity in SQLite
    skills_json: str = "[]" 
    experience_json: str = "[]"
    education_json: str = "[]"
    raw_text: str = Field() # Removed invalid defer argument
    filename: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    @property
    def skills(self) -> List[str]:
        return json.loads(self.skills_json)
    
    @skills.setter
    def skills(self, value: List[str]):
        self.skills_json = json.dumps(value)

    @property
    def experience(self) -> List[str]:
        return json.loads(self.experience_json)
    
    @experience.setter
    def experience(self, value: List[str]):
        self.experience_json = json.dumps(value)

    @property
    def education(self) -> List[str]:
        return json.loads(self.education_json)
    
    @education.setter
    def education(self, value: List[str]):
        self.education_json = json.dumps(value)

class InterviewMessage(SQLModel, table=True):
    """Database model for chat history"""
    id: Optional[int] = Field(default=None, primary_key=True)
    role: str
    content: str
    code_context: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class JobMatch(SQLModel, table=True):
    """Database model for job match history"""
    id: Optional[int] = Field(default=None, primary_key=True)
    candidate_id: int
    job_title: str
    match_score: float
    qualified: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow)
