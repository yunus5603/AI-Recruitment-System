import os
import tempfile

import edge_tts
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import StreamingResponse
from sqlmodel import Session, delete, select

from models.db import InterviewMessage, get_session
from models.schemas import ChatMessage, CodeExecutionRequest, CodeExecutionResult
from services import llm
from services.code_executor import execute_python_code

router = APIRouter(prefix="/interview", tags=["interview"])

HISTORY_WINDOW = 20

SYSTEM_PROMPT = """You are an expert technical interviewer for software development roles.
You can ask coding questions, review solutions, and provide feedback.
When appropriate, you can generate code examples or ask candidates to write code.
Be professional, encouraging, and thorough in your evaluation."""

DEMO_REPLY = (
    "Demo mode is on, so I can't run the AI interviewer (set GROQ_API_KEY to enable it). "
    "Here is a warm-up question instead: write a function that returns the first "
    "non-repeating character in a string, then run it in the editor."
)


def build_messages(history: list[InterviewMessage], code_context: str | None) -> list[dict[str, str]]:
    system = SYSTEM_PROMPT
    if code_context:
        system += (
            "\n\nThe user has the following code in their editor:\n"
            f"```python\n{code_context}\n```\nReference this code if the user asks about it."
        )
    messages = [{"role": "system", "content": system}]
    messages += [{"role": m.role, "content": m.content} for m in history]
    return messages


@router.post("/chat")
async def chat(message: ChatMessage, session: Session = Depends(get_session)):
    """Send a message to the AI interviewer. Both turns are persisted."""
    if message.role != "user":
        raise HTTPException(status_code=400, detail="Only user messages can be sent")

    session.add(InterviewMessage(role="user", content=message.content, code_context=message.code_context))
    session.commit()

    history = session.exec(
        select(InterviewMessage).order_by(InterviewMessage.id.desc()).limit(HISTORY_WINDOW)
    ).all()
    history = list(reversed(history))

    if llm.demo_mode():
        reply = DEMO_REPLY
    else:
        try:
            reply = await run_in_threadpool(
                llm.chat_completion,
                build_messages(history, message.code_context),
                temperature=0.7,
                max_tokens=2048,
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Interviewer failed: {e}") from e

    session.add(InterviewMessage(role="assistant", content=reply))
    session.commit()
    return {"message": reply}


@router.post("/execute-code", response_model=CodeExecutionResult)
async def execute_code(request: CodeExecutionRequest):
    """Run a Python snippet in the sandbox (see SECURITY.md)."""
    if request.language != "python":
        raise HTTPException(status_code=400, detail="Only Python is supported currently")
    return await run_in_threadpool(execute_python_code, request.code)


@router.get("/history")
async def get_chat_history(session: Session = Depends(get_session)):
    """Get the entire chat history"""
    msgs = session.exec(select(InterviewMessage).order_by(InterviewMessage.id)).all()
    return {"history": [{"role": m.role, "content": m.content, "code_context": m.code_context} for m in msgs]}


@router.delete("/clear-history")
async def clear_chat_history(session: Session = Depends(get_session)):
    """Clear the chat history"""
    session.exec(delete(InterviewMessage))
    session.commit()
    return {"message": "Chat history cleared"}


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcribe an audio clip with Groq Whisper."""
    content = await file.read()
    if len(content) < 100:
        raise HTTPException(status_code=400, detail="Audio file too small or empty")
    client = llm.get_client()
    if client is None:
        raise HTTPException(status_code=503, detail="Transcription needs GROQ_API_KEY")

    # A per-request temp file, so concurrent requests can't overwrite each other.
    with tempfile.NamedTemporaryFile(suffix=".webm") as tmp:
        tmp.write(content)
        tmp.flush()
        try:
            transcription = await run_in_threadpool(
                client.audio.transcriptions.create,
                file=(os.path.basename(tmp.name), content),
                model=llm.TRANSCRIBE_MODEL,
                response_format="json",
                language="en",
                temperature=0.0,
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Transcription failed: {e}") from e
    return {"text": transcription.text}


@router.post("/speak")
async def text_to_speech(text: str):
    """Convert text to speech with Edge TTS and stream the MP3."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text is empty")
    communicate = edge_tts.Communicate(text[:4000], "en-US-ChristopherNeural")

    async def audio_stream():
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]

    return StreamingResponse(audio_stream(), media_type="audio/mpeg")
