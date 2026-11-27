import json

import pytest

from models.schemas import JobDescription, ResumeData
from services import matcher

JOB = JobDescription(
    title="Backend Engineer",
    description="Build APIs",
    required_skills=["Python", "FastAPI", "PostgreSQL"],
    preferred_skills=["Docker", "AWS"],
)


def resume(*skills):
    return ResumeData(name="Jane", skills=list(skills), raw_text="")


def test_overlap_all_required_meets_threshold():
    result = matcher.score_by_skill_overlap(resume("python", "FastAPI", "PostgreSQL"), JOB)
    assert result.match_score == 80.0
    assert result.qualified
    assert result.missing_skills == []


def test_overlap_counts_preferred_and_missing():
    result = matcher.score_by_skill_overlap(resume("Python", "Docker"), JOB)
    assert result.match_score == pytest.approx(80 / 3 + 10, abs=0.1)
    assert result.missing_skills == ["FastAPI", "PostgreSQL"]
    assert not result.qualified


@pytest.mark.parametrize("raw,expected", [(150, 100.0), (-5, 0.0), ("85", 85.0), (None, 0.0)])
def test_clamp_score(raw, expected):
    assert matcher.clamp_score(raw) == expected


async def test_match_uses_llm_and_clamps(fake_llm):
    fake = fake_llm(
        json.dumps(
            {"match_score": 120, "matched_skills": ["Python"], "missing_skills": [], "justification": "ok"}
        )
    )
    result = await matcher.match_resume_to_job(resume("Python"), JOB)
    assert result.match_score == 100.0
    assert result.qualified
    prompt = fake.calls[0]["messages"][1]["content"]
    assert "Backend Engineer" in prompt and "PostgreSQL" in prompt


async def test_match_falls_back_to_overlap_in_demo_mode():
    result = await matcher.match_resume_to_job(resume("Python", "FastAPI", "PostgreSQL", "AWS"), JOB)
    assert result.match_score == 90.0
