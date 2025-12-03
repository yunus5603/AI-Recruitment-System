"""
Test script to reproduce the matching error
"""
import requests
import json

BASE_URL = "http://localhost:8000"

# Test data
job_description = {
    "title": "Senior Python Developer",
    "description": "We are looking for an experienced Python developer",
    "required_skills": ["Python", "FastAPI", "PostgreSQL"],
    "preferred_skills": ["Docker", "AWS"]
}

def test_match():
    """Test the matching endpoint"""
    print("Testing /candidates/match endpoint...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/candidates/match",
            json=job_description,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")

if __name__ == "__main__":
    test_match()
