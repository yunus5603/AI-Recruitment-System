"""Generate a sample resume PDF for trying the upload flow.

Usage: python scripts/create_sample_resume.py [output.pdf]
"""

import sys

from reportlab.pdfgen import canvas

LINES = [
    "Jane Doe",
    "jane.doe@example.com | +1 555 123 4567",
    "Senior Software Engineer",
    "Skills: Python, FastAPI, PostgreSQL, Docker, AWS, React",
    "Experience: 6 years building backend services and data pipelines",
    "Education: B.Sc. Computer Science",
]


def create_sample_resume(filename: str) -> None:
    c = canvas.Canvas(filename)
    y = 750
    for line in LINES:
        c.drawString(72, y, line)
        y -= 20
    c.save()


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "sample_resume.pdf"
    create_sample_resume(out)
    print(f"Created {out}")
