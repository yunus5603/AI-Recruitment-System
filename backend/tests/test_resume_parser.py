import json

import pytest

from services import resume_parser


def test_extract_text_from_pdf(resume_pdf):
    text = resume_parser.extract_text_from_pdf(str(resume_pdf))
    assert "Jane Doe" in text
    assert "FastAPI" in text


def test_extract_text_rejects_non_pdf(tmp_path):
    bad = tmp_path / "bad.pdf"
    bad.write_text("not a pdf")
    with pytest.raises(ValueError):
        resume_parser.extract_text_from_pdf(str(bad))


def test_heuristic_parser_finds_contact_details_and_skills():
    data = resume_parser.parse_resume_heuristically(
        "Jane Doe\njane@example.com | +1 555 123 4567\nSkills: Python, React, Go, Docker"
    )
    assert data.name == "Jane Doe"
    assert data.email == "jane@example.com"
    assert data.phone == "+1 555 123 4567"
    assert {"Python", "React", "Go", "Docker"} <= set(data.skills)
    # "Go" must match as a word, not inside other words
    assert "Go" not in resume_parser.parse_resume_heuristically("Good at Django").skills


async def test_parse_resume_uses_llm_when_configured(fake_llm, resume_pdf):
    fake = fake_llm(
        "```json\n"
        + json.dumps(
            {
                "name": "Jane Doe",
                "email": "jane.doe@example.com",
                "phone": "555",
                "skills": ["Python", "FastAPI"],
                "experience": ["6 years backend"],
                "education": ["B.Sc. CS"],
            }
        )
        + "\n```"
    )
    data = await resume_parser.parse_resume(str(resume_pdf))
    assert data.skills == ["Python", "FastAPI"]
    assert "Jane Doe" in data.raw_text
    assert "Jane Doe" in fake.calls[0]["messages"][1]["content"]


async def test_parse_resume_reports_invalid_llm_json(fake_llm, resume_pdf):
    fake_llm("I cannot help with that")
    with pytest.raises(ValueError, match="invalid JSON"):
        await resume_parser.parse_resume(str(resume_pdf))
