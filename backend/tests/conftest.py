import os
import sys
from pathlib import Path
from types import SimpleNamespace

# Configure before the app modules are imported: an isolated database and no
# real API key, so nothing in the suite can reach Groq.
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(__file__).parent / ".test.db")
os.environ.pop("GROQ_API_KEY", None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import SQLModel  # noqa: E402

from main import app  # noqa: E402
from models.db import engine  # noqa: E402
from services import llm  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    llm.get_client.cache_clear()
    yield


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class FakeGroq:
    """Stands in for the Groq client and returns queued replies in order."""

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self._create))

    def _create(self, **kwargs):
        self.calls.append(kwargs)
        content = self.replies.pop(0)
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])


@pytest.fixture
def fake_llm(monkeypatch):
    """Switch the app out of demo mode with a fake LLM: ``fake_llm(reply, ...)``."""

    def install(*replies):
        fake = FakeGroq(replies)
        monkeypatch.setattr(llm, "get_client", lambda: fake)
        return fake

    return install


@pytest.fixture
def resume_pdf(tmp_path):
    from scripts.create_sample_resume import create_sample_resume

    path = tmp_path / "resume.pdf"
    create_sample_resume(str(path))
    return path
