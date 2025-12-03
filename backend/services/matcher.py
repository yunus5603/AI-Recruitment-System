import os
from groq import Groq
from models.schemas import ResumeData, JobDescription, MatchResult
import json
from dotenv import load_dotenv
load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


async def match_resume_to_job(resume: ResumeData, job: JobDescription) -> MatchResult:
    """
    Match a resume against a job description and calculate a match score.
    Returns a MatchResult with score, matched/missing skills, and justification.
    """
    
    prompt = f"""
    You are an expert recruiter. Analyze how well this candidate matches the job requirements.
    
    Job Title: {job.title}
    Job Description: {job.description}
    Required Skills: {', '.join(job.required_skills)}
    Preferred Skills: {', '.join(job.preferred_skills or [])}
    
    Candidate Name: {resume.name or 'Unknown'}
    Candidate Skills: {', '.join(resume.skills)}
    Candidate Experience: {' | '.join(resume.experience[:3])}  # First 3 experiences
    
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
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert technical recruiter. Analyze candidate-job matches objectively and return valid JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1024
        )

        
        # Parse the JSON response
        result = json.loads(response.choices[0].message.content)
        
        match_score = result["match_score"]
        
        return MatchResult(
            candidate_name=resume.name,
            match_score=match_score,
            matched_skills=result["matched_skills"],
            missing_skills=result["missing_skills"],
            justification=result["justification"],
            qualified=match_score >= 80  # 80% threshold
        )
    except Exception as e:
        raise Exception(f"Error matching resume to job: {str(e)}")
