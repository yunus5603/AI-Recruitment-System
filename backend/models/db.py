import json
import os
from datetime import UTC, datetime

from sqlmodel import Field, Session, SQLModel, create_engine

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///recruitment.db")

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, echo=False, connect_args=_connect_args)


def _now() -> datetime:
    return datetime.now(UTC)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


class Candidate(SQLModel, table=True):
    """Database model for candidates"""

    id: int | None = Field(default=None, primary_key=True)
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    # Lists are stored as JSON strings for simplicity in SQLite
    skills_json: str = "[]"
    experience_json: str = "[]"
    education_json: str = "[]"
    raw_text: str
    filename: str
    created_at: datetime = Field(default_factory=_now)

    @property
    def skills(self) -> list[str]:
        return json.loads(self.skills_json)

    @property
    def experience(self) -> list[str]:
        return json.loads(self.experience_json)

    @property
    def education(self) -> list[str]:
        return json.loads(self.education_json)


class InterviewMessage(SQLModel, table=True):
    """Database model for chat history"""

    id: int | None = Field(default=None, primary_key=True)
    role: str
    content: str
    code_context: str | None = None
    timestamp: datetime = Field(default_factory=_now)


class JobMatch(SQLModel, table=True):
    """Database model for job match history"""

    id: int | None = Field(default=None, primary_key=True)
    candidate_id: int
    job_title: str
    match_score: float
    qualified: bool
    timestamp: datetime = Field(default_factory=_now)
