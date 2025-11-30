from fastapi import APIRouter, HTTPException
from models.schemas import ChatMessage, CodeExecutionRequest, CodeExecutionResult
from services.code_executor import execute_python_code
from groq import Groq
import os
from typing import List

router = APIRouter(prefix="/interview", tags=["interview"])

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


# In-memory chat history (in production, use a database)
chat_history: List[ChatMessage] = []

@router.post("/chat")
async def chat(message: ChatMessage):
    """
    Send a message to the AI interviewer and get a response.
    """
    # Add user message to history
    chat_history.append(message)
    
    # Prepare messages for OpenAI
    messages = [
        {
            "role": "system", 
            "content": """You are an expert technical interviewer for software development roles. 
            You can ask coding questions, review solutions, and provide feedback.
            When appropriate, you can generate code examples or ask candidates to write code.
            Be professional, encouraging, and thorough in your evaluation."""
        }
    ]
    
    # Add chat history
    for msg in chat_history:
        messages.append({"role": msg.role, "content": msg.content})
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.7,
            max_tokens=2048
        )

        
        assistant_message = response.choices[0].message.content
        
        # Add assistant response to history
        chat_history.append(ChatMessage(role="assistant", content=assistant_message))
        
        return {"message": assistant_message}
        
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
async def get_chat_history():
    """Get the entire chat history"""
    return {"history": chat_history}

@router.delete("/clear-history")
async def clear_chat_history():
    """Clear the chat history"""
    chat_history.clear()
    return {"message": "Chat history cleared"}
