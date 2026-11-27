import re

from pypdf import PdfReader

from models.schemas import ResumeData
from services import llm

SYSTEM_PROMPT = (
    "You are a resume parsing assistant. Extract structured data from resumes and return valid JSON only."
)

PROMPT_TEMPLATE = """
Extract the following information from this resume and return it as JSON:
- name (string)
- email (string)
- phone (string)
- skills (array of strings)
- experience (array of strings, each entry should be a brief description)
- education (array of strings)

Resume text:
{raw_text}

Return ONLY valid JSON, no additional text.
"""

# Used by the offline (demo mode) parser to recognise common skills.
KNOWN_SKILLS = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "Go",
    "Rust",
    "C++",
    "C#",
    "SQL",
    "React",
    "Next.js",
    "Vue",
    "Angular",
    "Node.js",
    "FastAPI",
    "Django",
    "Flask",
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
    "Docker",
    "Kubernetes",
    "AWS",
    "GCP",
    "Azure",
    "Terraform",
    "Git",
    "Linux",
    "Machine Learning",
    "Deep Learning",
    "PyTorch",
    "TensorFlow",
    "scikit-learn",
    "Pandas",
    "NumPy",
    "LangChain",
    "NLP",
    "LLM",
    "RAG",
    "Spark",
    "Kafka",
    "GraphQL",
    "REST",
    "CI/CD",
    "Tailwind",
]

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file."""
    try:
        reader = PdfReader(file_path)
        return "\n".join((page.extract_text() or "") for page in reader.pages).strip()
    except Exception as e:
        raise ValueError(f"Could not read PDF: {e}") from e


def parse_resume_heuristically(raw_text: str) -> ResumeData:
    """Best-effort structured extraction without an LLM (demo mode)."""
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    email = EMAIL_RE.search(raw_text)
    phone = PHONE_RE.search(raw_text)
    lowered = raw_text.lower()
    skills = [s for s in KNOWN_SKILLS if re.search(rf"(?<![\w]){re.escape(s.lower())}(?![\w])", lowered)]
    return ResumeData(
        name=lines[0] if lines else None,
        email=email.group(0) if email else None,
        phone=phone.group(0).strip() if phone else None,
        skills=skills,
        experience=[],
        education=[],
        raw_text=raw_text,
    )


def parse_llm_reply(content: str, raw_text: str) -> ResumeData:
    data = llm.extract_json(content)
    return ResumeData(
        name=data.get("name"),
        email=data.get("email"),
        phone=data.get("phone"),
        skills=[str(s) for s in data.get("skills") or []],
        experience=[str(s) for s in data.get("experience") or []],
        education=[str(s) for s in data.get("education") or []],
        raw_text=raw_text,
    )


async def parse_resume(file_path: str) -> ResumeData:
    """Parse a resume PDF into structured data."""
    raw_text = extract_text_from_pdf(file_path)
    if not raw_text:
        raise ValueError("No text found in PDF (is it a scanned image?)")

    if llm.demo_mode():
        return parse_resume_heuristically(raw_text)

    content = llm.chat_completion(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": PROMPT_TEMPLATE.format(raw_text=raw_text)},
        ],
        temperature=0.3,
        max_tokens=1024,
    )
    try:
        return parse_llm_reply(content, raw_text)
    except ValueError as e:
        raise ValueError(f"Model returned invalid JSON: {e}") from e
