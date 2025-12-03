import os
from pypdf import PdfReader
from groq import Groq
from models.schemas import ResumeData
import json
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file"""
    try:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

async def parse_resume(file_path: str) -> ResumeData:
    """Parse resume and extract structured data using OpenAI"""
    # Extract raw text
    raw_text = extract_text_from_pdf(file_path)
    
    # Use OpenAI to structure the data
    prompt = f"""
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
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a resume parsing assistant. Extract structured data from resumes and return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )
        
        # Parse the JSON response
        content = response.choices[0].message.content
        
        # Clean up markdown code blocks if present
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0]
        elif "```" in content:
            content = content.split("```")[1]
            
        structured_data = json.loads(content.strip())

        
        return ResumeData(
            name=structured_data.get("name"),
            email=structured_data.get("email"),
            phone=structured_data.get("phone"),
            skills=structured_data.get("skills", []),
            experience=structured_data.get("experience", []),
            education=structured_data.get("education", []),
            raw_text=raw_text
        )
    except Exception as e:
        raise Exception(f"Error parsing resume with OpenAI: {str(e)}")
