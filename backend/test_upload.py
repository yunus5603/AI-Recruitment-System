import requests

url = "http://localhost:8000/candidates/upload-resume"
files = {'file': open('dummy_resume.pdf', 'rb')}

try:
    response = requests.post(url, files=files)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
