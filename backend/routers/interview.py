from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatMessage, CodeExecutionRequest, CodeExecutionResult
from services.code_executor import execute_python_code
from groq import Groq
import os
from typing import List
from sqlmodel import Session, select
from models.db import get_session, InterviewMessage

router = APIRouter(prefix="/interview", tags=["interview"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

@router.post("/chat")
async def chat(
    message: ChatMessage,
    session: Session = Depends(get_session)
):
    """
    Send a message to the AI interviewer and get a response.
    Persists messages to database.
    """
    # Save user message
    user_msg_db = InterviewMessage(
        role=message.role,
        content=message.content,
        code_context=message.code_context
    )
    session.add(user_msg_db)
    session.commit()
    
    # Retrieve recent history from DB for context (limit to last 20 messages for prompt context)
    history_msgs = session.exec(select(InterviewMessage).order_by(InterviewMessage.timestamp.desc()).limit(20)).all()
    history_msgs.reverse() # Order by time ascending
    
    # Context-aware system prompt
    context_instruction = ""
    if message.code_context:
        context_instruction = f"\n\nThe user has the following code in their editor:\n```python\n{message.code_context}\n```\nReference this code if the user asks about it."
    
    # Prepare messages for OpenAI
    messages = [
        {
            "role": "system", 
            "content": f"""You are an expert technical interviewer for software development roles. 
            You can ask coding questions, review solutions, and provide feedback.
            When appropriate, you can generate code examples or ask candidates to write code.
            Be professional, encouraging, and thorough in your evaluation.{context_instruction}"""
        }
    ]
    
    # Add chat history
    for msg in history_msgs:
        messages.append({"role": msg.role, "content": msg.content})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )

        
        assistant_message_content = response.choices[0].message.content
        
        # Save assistant response to DB
        assistant_msg_db = InterviewMessage(
            role="assistant",
            content=assistant_message_content
        )
        session.add(assistant_msg_db)
        session.commit()
        
        return {"message": assistant_message_content}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-code", response_model=CodeExecutionResult)
async def execute_code(request: CodeExecutionRequest):
    """
    Execute Python code and return the result.
    WARNING: This is not secure for production use.
    """
    if request.language != "python":
        raise HTTPException(status_code=400, detail="Only Python is supported currently")
    
    try:
        result = execute_python_code(request.code)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_chat_history(session: Session = Depends(get_session)):
    """Get the entire chat history"""
    msgs = session.exec(select(InterviewMessage).order_by(InterviewMessage.timestamp)).all()
    return {"history": [
        {"role": m.role, "content": m.content, "code_context": m.code_context} for m in msgs
    ]}

@router.delete("/clear-history")
async def clear_chat_history(session: Session = Depends(get_session)):
    """Clear the chat history"""
    msgs = session.exec(select(InterviewMessage)).all()
    for m in msgs:
        session.delete(m)
    session.commit()
    return {"message": "Chat history cleared"}

from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
import edge_tts
import io

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...)
):
    """
    Transcribe audio file using Groq Whisper.
    """
    try:
        # Save temp file for Groq client (requires file path)
        with open("temp_audio.webm", "wb") as buffer:
            content = await file.read()
            file_size = len(content)
            print(f"DEBUG: Received audio file. Size: {file_size} bytes. Content-Type: {file.content_type}")
            
            if file_size < 100:
                raise HTTPException(status_code=400, detail="Audio file too small or empty")
                
            buffer.write(content)
            
        with open("temp_audio.webm", "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=("temp_audio.webm", audio_file.read()),
                model="whisper-large-v3",
                response_format="json",
                language="en",
                temperature=0.0
            )
        
        return {"text": transcription.text}
        return {"text": transcription.text}
    except Exception as e:
        print(f"TRANSCRIBE ERROR: {str(e)}") # Debug logging
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists("temp_audio.webm"):
            os.remove("temp_audio.webm")

@router.post("/speak")
async def text_to_speech(
    text: str
):
    """
    Convert text to speech using Edge TTS.
    Returns streaming audio response.
    """
    try:
        communicate = edge_tts.Communicate(text, "en-US-ChristopherNeural")
        
        # Generator for streaming response
        async def audio_stream():
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    yield chunk["data"]
                    
        return StreamingResponse(audio_stream(), media_type="audio/mp3")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
