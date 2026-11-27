from models.schemas import JobDescription, MatchResult, ResumeData
from services import llm

QUALIFY_THRESHOLD = 80.0

SYSTEM_PROMPT = (
    "You are an expert technical recruiter. Analyze candidate-job matches "
    "objectively and return valid JSON only."
)

PROMPT_TEMPLATE = """
You are an expert recruiter. Analyze how well this candidate matches the job requirements.

Job Title: {title}
Job Description: {description}
Required Skills: {required}
Preferred Skills: {preferred}

Candidate Name: {name}
Candidate Skills: {skills}
Candidate Experience: {experience}

Provide:
1. A match score from 0-100 (where 100 is a perfect match)
2. List of matched skills (skills the candidate has that match the job requirements)
3. List of missing skills (required skills the candidate lacks)
4. A brief justification (2-3 sentences) explaining the score

Return ONLY valid JSON in this format:
{{
    "match_score": <number>,
    "matched_skills": [<array of strings>],
    "missing_skills": [<array of strings>],
    "justification": "<string>"
}}
"""


def _norm(skill: str) -> str:
    return skill.strip().lower()


def clamp_score(value: object) -> float:
    try:
        score = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0
    return max(0.0, min(100.0, score))


def score_by_skill_overlap(resume: ResumeData, job: JobDescription) -> MatchResult:
    """Deterministic scoring used in demo mode.

    Required skills carry 80% of the score and preferred skills 20%, so a
    candidate with every required skill and none of the preferred ones scores
    exactly the qualifying threshold.
    """
    have = {_norm(s) for s in resume.skills}
    required = job.required_skills
    preferred = job.preferred_skills or []

    matched_req = [s for s in required if _norm(s) in have]
    matched_pref = [s for s in preferred if _norm(s) in have]
    missing = [s for s in required if _norm(s) not in have]

    req_part = 80.0 * len(matched_req) / len(required) if required else 80.0
    pref_part = 20.0 * len(matched_pref) / len(preferred) if preferred else 0.0
    score = round(req_part + pref_part, 1)

    return MatchResult(
        candidate_name=resume.name,
        match_score=score,
        matched_skills=matched_req + matched_pref,
        missing_skills=missing,
        justification=(
            f"Has {len(matched_req)}/{len(required)} required and "
            f"{len(matched_pref)}/{len(preferred)} preferred skills "
            "(offline skill-overlap scoring)."
        ),
        qualified=score >= QUALIFY_THRESHOLD,
    )


def build_prompt(resume: ResumeData, job: JobDescription) -> str:
    return PROMPT_TEMPLATE.format(
        title=job.title,
        description=job.description,
        required=", ".join(job.required_skills),
        preferred=", ".join(job.preferred_skills or []),
        name=resume.name or "Unknown",
        skills=", ".join(resume.skills),
        experience=" | ".join(resume.experience[:3]),
    )


def parse_llm_reply(content: str, resume: ResumeData) -> MatchResult:
    data = llm.extract_json(content)
    score = clamp_score(data.get("match_score"))
    return MatchResult(
        candidate_name=resume.name,
        match_score=score,
        matched_skills=[str(s) for s in data.get("matched_skills") or []],
        missing_skills=[str(s) for s in data.get("missing_skills") or []],
        justification=str(data.get("justification") or ""),
        qualified=score >= QUALIFY_THRESHOLD,
    )


async def match_resume_to_job(resume: ResumeData, job: JobDescription) -> MatchResult:
    """Score a resume against a job description."""
    if llm.demo_mode():
        return score_by_skill_overlap(resume, job)

    content = llm.chat_completion(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_prompt(resume, job)},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    try:
        return parse_llm_reply(content, resume)
    except ValueError as e:
        raise ValueError(f"Model returned invalid JSON: {e}") from e
