# AI Recruitment System

A smart recruitment system that automates resume screening and provides an advanced technical interview interface powered by AI.

## Features

### 🎯 Core Capabilities
- **Resume Parsing**: Automatically extract structured data from PDF resumes using AI
- **Job Matching**: Compare candidates against job descriptions with AI-powered analysis
- **Candidate Ranking**: Automatically rank candidates based on match scores (≥80% threshold)
- **AI Interview Chat**: Conduct technical interviews with an AI interviewer
- **Code Execution**: Run Python code snippets during interviews with live output

### 🎨 Modern UI
- Beautiful glassmorphism design with gradient accents
- Responsive layout for desktop and mobile
- Real-time feedback and animations
- Dark mode optimized

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Groq (Llama 3.3 70B)**: AI-powered resume parsing, matching, and chat
- **pypdf**: PDF text extraction
- **Pydantic**: Data validation

### Frontend
- **React**: UI library
- **Vite**: Fast build tool
- **TailwindCSS**: Utility-first CSS framework
- **Inter Font**: Modern typography

## Project Structure

```
AI-Recruitment-System/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   ├── services/
│   │   ├── resume_parser.py    # Resume parsing logic
│   │   ├── matcher.py          # Job matching logic
│   │   └── code_executor.py    # Code execution service
│   ├── routers/
│   │   ├── candidates.py       # Candidate endpoints
│   │   └── interview.py        # Interview endpoints
│   ├── requirements.txt
│   └── .env                    # Environment variables
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ResumeUpload.jsx
│   │   │   ├── JobDescriptionInput.jsx
│   │   │   ├── CandidateList.jsx
│   │   │   └── ChatInterface.jsx
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   └── Interview.jsx
│   │   ├── App.jsx
│   │   └── index.css
│   └── package.json
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.12+
- Node.js 20+
- Groq API Key

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   - Create `backend/.env` file and add your Groq API key:
     ```
     GROQ_API_KEY=your_actual_api_key_here
     ```
   - Get your free API key from: https://console.groq.com/keys

4. **Run the backend server**:
   ```bash
   uvicorn main:app --reload
   ```
   
   The API will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install npm dependencies**:
   ```bash
   npm install
   ```

3. **Run the development server**:
   ```bash
   npm run dev
   ```
   
   The app will be available at `http://localhost:5173`

## Usage Guide

### 1. Upload Resumes
- Navigate to the **Dashboard** page
- Drag and drop PDF resumes or click to browse
- The system will automatically parse and extract candidate information

### 2. Match Candidates
- Fill in the job description form:
  - Job Title
  - Job Description
  - Required Skills (comma-separated)
  - Preferred Skills (comma-separated)
- Click "Match Candidates"
- View ranked candidates who meet the ≥80% threshold

### 3. Conduct Interviews
- Navigate to the **Interview** page
- Use the AI chat to ask technical questions
- Write and execute Python code in the code executor
- Review execution results in real-time

## API Endpoints

### Candidates
- `POST /candidates/upload-resume` - Upload and parse a resume
- `POST /candidates/match` - Match candidates to a job description
- `GET /candidates/all` - Get all uploaded candidates
- `DELETE /candidates/clear` - Clear all candidates

### Interview
- `POST /interview/chat` - Send a message to the AI interviewer
- `POST /interview/execute-code` - Execute Python code
- `GET /interview/history` - Get chat history
- `DELETE /interview/clear-history` - Clear chat history

## Security Considerations

> ⚠️ **WARNING**: The code execution feature in this MVP runs code directly in the Python process. This is **NOT secure** for production use.

For production deployment, implement:
- Sandboxed execution environments (Docker, gVisor, or similar)
- Rate limiting
- Input validation and sanitization
- User authentication and authorization
- Secure API key management

## Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and multi-tenancy
- [ ] Secure code execution sandbox
- [ ] Support for DOCX resumes
- [ ] Email notifications
- [ ] Interview recording and playback
- [ ] Advanced analytics dashboard
- [ ] Multi-language support for code execution

## License

MIT

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
