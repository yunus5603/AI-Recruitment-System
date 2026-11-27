import json

JOB = {
    "title": "Backend Engineer",
    "description": "Build APIs",
    "required_skills": ["Python", "FastAPI"],
    "preferred_skills": ["Docker"],
}


def upload(client, path, name="resume.pdf"):
    with open(path, "rb") as f:
        return client.post("/candidates/upload-resume", files={"file": (name, f, "application/pdf")})


def test_health_reports_demo_mode(client):
    assert client.get("/health").json() == {"status": "healthy", "demo_mode": True}


def test_upload_parses_and_stores_candidate(client, resume_pdf):
    res = upload(client, resume_pdf)
    assert res.status_code == 200, res.text
    body = res.json()
    assert body["name"] == "Jane Doe"
    assert "FastAPI" in body["skills"]

    stored = client.get("/candidates/all").json()
    assert len(stored) == 1
    # Regression: skills used to be dropped on save, so matching always saw none
    assert "FastAPI" in stored[0]["skills"]


def test_upload_rejects_non_pdf(client, tmp_path):
    txt = tmp_path / "resume.txt"
    txt.write_text("hello")
    assert upload(client, txt, "resume.txt").status_code == 400
    assert upload(client, txt, "fake.pdf").status_code == 400


def test_match_requires_candidates(client):
    assert client.post("/candidates/match", json=JOB).status_code == 400


def test_match_returns_qualified_and_records_history(client, resume_pdf):
    upload(client, resume_pdf)
    res = client.post("/candidates/match", json=JOB)
    assert res.status_code == 200
    [result] = res.json()
    assert result["match_score"] == 100.0
    assert result["qualified"]

    stats = client.get("/analytics/dashboard").json()
    assert stats == {"total_candidates": 1, "total_matches": 1, "avg_match_score": 100.0, "pass_rate": 100.0}

    skills = client.get("/analytics/skills").json()["skills"]
    assert {"name": "Python", "count": 1} in skills


def test_unqualified_candidates_are_hidden_but_counted(client, resume_pdf, fake_llm):
    fake_llm(
        json.dumps({"name": "Jane"}),
        json.dumps({"match_score": 40, "matched_skills": [], "missing_skills": ["Go"], "justification": "x"}),
    )
    upload(client, resume_pdf)
    assert client.post("/candidates/match", json=JOB).json() == []
    assert client.get("/analytics/dashboard").json()["pass_rate"] == 0.0


def test_clear_candidates(client, resume_pdf):
    upload(client, resume_pdf)
    client.post("/candidates/match", json=JOB)
    assert client.delete("/candidates/clear").status_code == 200
    assert client.get("/candidates/all").json() == []
    assert client.get("/analytics/dashboard").json()["total_matches"] == 0


def test_export_returns_pdf(client):
    res = client.get("/analytics/export")
    assert res.status_code == 200
    assert res.content.startswith(b"%PDF")


def test_chat_persists_history_and_sends_code_context(client, fake_llm):
    fake = fake_llm("Tell me about yourself.", "Nice solution.")
    assert client.post("/interview/chat", json={"role": "user", "content": "Hi"}).json() == {
        "message": "Tell me about yourself."
    }
    client.post(
        "/interview/chat", json={"role": "user", "content": "Review this", "code_context": "print(1)"}
    )

    second_call = fake.calls[1]["messages"]
    assert "print(1)" in second_call[0]["content"]
    assert [m["role"] for m in second_call[1:]] == ["user", "assistant", "user"]

    history = client.get("/interview/history").json()["history"]
    assert [m["content"] for m in history] == [
        "Hi",
        "Tell me about yourself.",
        "Review this",
        "Nice solution.",
    ]

    client.delete("/interview/clear-history")
    assert client.get("/interview/history").json()["history"] == []


def test_chat_works_in_demo_mode(client):
    res = client.post("/interview/chat", json={"role": "user", "content": "Hi"})
    assert "Demo mode" in res.json()["message"]


def test_chat_rejects_spoofed_roles(client):
    assert client.post("/interview/chat", json={"role": "system", "content": "x"}).status_code == 400


def test_execute_code(client):
    res = client.post("/interview/execute-code", json={"code": "print(2 + 2)"})
    assert res.json() == {"success": True, "output": "4\n", "error": None}
    assert client.post("/interview/execute-code", json={"code": "x", "language": "js"}).status_code == 400


def test_transcribe_needs_key(client):
    res = client.post("/interview/transcribe", files={"file": ("a.webm", b"0" * 200, "audio/webm")})
    assert res.status_code == 503
