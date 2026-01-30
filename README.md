# AI Mock Interview Platform

A full-stack AI-powered mock interview platform featuring voice integration, real-time feedback, and LLM-based analysis. The platform helps users practice interview skills with intelligent feedback, performance metrics, and professional ATS resume analysis.

## 📑 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)

## 🌟 Overview

This platform provides an immersive mock interview experience with:
- **Two-Round Interview Structure**: Round 1 (Behavioral - Voice) + Round 2 (Technical - Coding)
- **Voice-enabled behavioral interviews** using VAPI integration
- **Technical coding challenges** with integrated Monaco code editor
- **LLM-powered feedback** using Google Gemini 2.5 Flash (direct API integration)
- **ATS Resume Analyzer** with 6-parameter scoring system and file upload support (PDF/DOCX/TXT)
- **Multiple interview types**: Technical (Software, Data Science), Behavioral, and Company-specific
- **Real-time transcript** with clear speaker differentiation (User vs Interviewer)
- **Comprehensive reporting** with segregated Round 1/Round 2 performance metrics

## ✨ Features

### Interview Flow
- 🎯 **Round 1 - Behavioral Interview**: Voice-powered interview with VAPI AI
- 💻 **Round 2 - Technical Interview**: Coding challenges with Monaco code editor
- 📊 **Segregated Performance Reports**: Separate feedback for each round with tabbed interface

### Frontend (Next.js)
- 🎨 Modern, responsive UI with Tailwind CSS
- 🎙️ Voice interview interface with VAPI integration
- 💻 **Monaco Code Editor** for technical round with syntax highlighting
- 📝 **Resume Analyzer** with file upload (PDF, DOCX, TXT)
- 💬 Structured real-time transcript with speaker differentiation (no duplicate words)
- 📊 Real-time performance dashboard with Round 1/Round 2 tabs
- 📈 Interactive charts and visualizations
- 🎯 Multiple interview types and difficulty levels
- 📱 Mobile-responsive design
- 🌓 Dark mode support

### Backend (FastAPI)
- 🚀 High-performance RESTful API
- 🤖 **LLM-powered analysis** using Google Gemini 2.5 Flash (direct SDK integration)
- 💻 **Technical Code Evaluation**: Time/space complexity, correctness, best practices scoring
- 📄 **ATS Resume Analysis** with authoritative 6-parameter scoring system
- 📁 **File parsing** for PDF (PyPDF2), DOCX (python-docx), and TXT files
- 📝 Comprehensive question database (50+ questions)
- 🔊 VAPI webhook integration for voice processing
- 💾 SQLite database with session management
- 📊 Advanced analytics and metrics
- 🔐 Secure API endpoints
- 📖 Automatic API documentation (Swagger/ReDoc)

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (React 19)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI, shadcn/ui
- **Code Editor**: Monaco Editor (VS Code engine)
- **State Management**: React Hooks
- **Voice Integration**: VAPI SDK (@vapi-ai/web)
- **Animations**: Framer Motion, React Three Fiber
- **Charts**: Recharts
- **Icons**: Tabler Icons

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.13+
- **Database**: SQLite (SQLAlchemy ORM)
- **LLM Provider**: Google Gemini 2.5 Flash (direct SDK via google.generativeai)
- **File Processing**: PyPDF2, python-docx
- **Voice Processing**: VAPI webhooks
- **Configuration**: python-dotenv, pydantic
- **ML Framework**: scikit-learn
- **NLP**: NLTK
- **Data Processing**: Pandas, NumPy
- **API**: HTTPX, Requests
- **Testing**: Pytest

## 📁 Project Structure

```
Mock Interview/
├── ai-mock-interview-frontend/     # Next.js frontend application
│   ├── src/
│   │   ├── app/                    # Next.js app router pages
│   │   │   ├── interview/          # Round 1 - Behavioral voice interview
│   │   │   ├── technical/          # Round 2 - Technical coding interview
│   │   │   ├── feedback/           # Performance reports (Round 1 & 2 tabs)
│   │   │   └── api/                # Next.js API routes
│   │   ├── components/             # Reusable React components
│   │   ├── hooks/                  # Custom React hooks
│   │   ├── lib/                    # Utility functions and configurations
│   │   ├── types/                  # TypeScript type definitions
│   │   └── data/                   # Static data and configurations
│   ├── public/                     # Static assets
│   └── package.json                # Frontend dependencies
│
├── ai-mock-interview-backend/      # FastAPI backend application
│   ├── app/
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── models.py               # SQLAlchemy models (InterviewSession, TechnicalSubmission)
│   │   ├── database.py             # Database configuration
│   │   ├── vapi_service.py         # VAPI integration service
│   │   ├── vapi_interview_service.py # Interview analyzer with Gemini
│   │   ├── gcp_gemini_service.py   # Google Gemini direct SDK service
│   │   ├── resume_service.py       # LLM resume analysis service
│   │   └── file_parser.py          # PDF/DOCX/TXT file parsing utility
│   ├── data/
│   │   └── interview-questions.json # Question database
│   ├── tests/                      # Test files
│   ├── .env                        # Environment configuration
│   └── requirements.txt            # Python dependencies
│
└── README.md                       # This file
```

## 🚀 Getting Started

### Quick Setup

📖 **For detailed setup instructions, see [SETUP.md](./SETUP.md)**

### Prerequisites

- **Node.js** 18+ and npm/bun
- **Python** 3.8+
- **Google Cloud Account** with Gemini API key ([Get it here](https://aistudio.google.com/apikey))
- **VAPI Account** and API key ([Get it here](https://vapi.ai)) - For voice features
- **ngrok** (optional) - For VAPI webhooks in development

### Quick Start

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd "Mock Interview"
```

#### 2. Backend Setup

```bash
cd ai-mock-interview-backend
python -m venv .venv
.venv\Scripts\activate  # Windows | source .venv/bin/activate (macOS/Linux)
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your Google Gemini API key and VAPI credentials
uvicorn app.main:app --reload
```

#### 3. Frontend Setup

```bash
cd ai-mock-interview-frontend
npm install  # or bun install
cp .env.example .env.local
# Edit .env.local with your VAPI credentials
npm run dev  # or bun dev
```

#### 4. (Optional) Setup ngrok for VAPI Webhooks
```bash
# In a separate terminal
ngrok http 8000
# Copy the https URL and update VAPI assistant settings
```

#### 5. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Environment Variables

**Backend** (`.env`):
```env
# Database
DATABASE_URL=sqlite:///./interview_platform.db

# Google Gemini Configuration (Direct SDK)
GOOGLE_API_KEY=your_google_gemini_api_key

# VAPI Configuration (Required for voice features)
VAPI_API_KEY=your_private_key
VAPI_WEBHOOK_SECRET=your_webhook_secret
BACKEND_URL=http://localhost:8000  # Or your ngrok URL

# Application
DEBUG=True
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_VAPI_PUBLIC_KEY=pk_your_public_key
NEXT_PUBLIC_VAPI_ASSISTANT_ID=asst_your_assistant_id
NEXT_PUBLIC_API_URL=http://localhost:8000
```

📖 **For detailed configuration guide, see [SETUP.md](./SETUP.md)**

### Running the Application

#### Start Backend Server

```bash
cd ai-mock-interview-backend
.venv\Scripts\activate  # Windows | source .venv/bin/activate (macOS/Linux)

# Run with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend API will be available at:
- **API**: http://localhost:8000
- **Swagger Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

#### Start Frontend Development Server

```bash
cd ai-mock-interview-frontend

# Run development server
npm run dev
```

### Database Setup

**SQLite** (default and recommended):
- No additional setup required
- Database file: `interview_platform.db`
- Automatically created on first run
- Tables: `interview_sessions`, `technical_submissions`

### LLM Configuration

The platform uses **Google Gemini 2.5 Flash** directly via the `google.generativeai` SDK:

- **Model**: `gemini-2.5-flash` (fast, accurate, cost-effective)
- **API Key**: Get from [Google AI Studio](https://aistudio.google.com/apikey)
- **Usage**: Interview analysis, code evaluation, resume analysis

### VAPI Setup

1. Create a VAPI account at [vapi.ai](https://vapi.ai)
2. Create an assistant with your interview prompts
3. Get your public key (starts with `pk_`) and assistant ID
4. For webhooks, use ngrok to expose your local backend
5. Configure webhook URL in VAPI dashboard: `https://your-ngrok-url.ngrok.io/api/v1/vapi/webhook`

## 📚 API Documentation

### Main Endpoints

#### Start Interview Session
```http
POST /api/v1/interview/start
Content-Type: application/json

{
  "interview_type": "behavioral",
  "difficulty": "intermediate",
  "duration": 30,
  "company": "Optional Company Name"
}

Response:
{
  "session_id": "uuid",
  "questions": [...],
  "interview_type": "behavioral"
}
```

#### Get Interview Results (Round 1 - Behavioral)
```http
GET /api/v1/interview/results/{session_id}

Response:
{
  "session_id": "uuid",
  "interview_type": "behavioral",
  "overall_score": 85,
  "strengths": [...],
  "improvements": [...],
  "transcript": [...]
}
```

#### Submit Technical Code (Round 2)
```http
POST /api/v1/technical/submit
Content-Type: application/json

{
  "session_id": "uuid",
  "question_title": "Two Sum",
  "question_description": "Given an array...",
  "code": "def two_sum(nums, target): ...",
  "language": "python"
}

Response:
{
  "success": true,
  "scores": {
    "correctness": 90,
    "efficiency": 85,
    "code_quality": 88,
    "best_practices": 80
  },
  "overall_score": 86,
  "time_complexity": "O(n)",
  "space_complexity": "O(n)",
  "strengths": [...],
  "improvements": [...],
  "feedback": "Detailed code review..."
}
```

#### Get Technical Results (Round 2)
```http
GET /api/v1/technical/results/{session_id}

Response:
{
  "session_id": "uuid",
  "submissions": [
    {
      "question_title": "Two Sum",
      "code": "...",
      "language": "python",
      "overall_score": 86,
      ...
    }
  ]
}
```

#### Analyze Resume
```http
POST /api/resume/analyze
Content-Type: multipart/form-data

file: <resume.pdf/resume.docx/resume.txt>
job_description: "Optional job description for matching"
target_role: "Optional target role (e.g., Software Engineer)"
```

#### VAPI Webhook
```http
POST /api/v1/vapi/webhook
```

For complete API documentation, visit http://localhost:8000/docs after starting the backend server.

## 💻 Development

### Backend Development

```bash
# Run tests
pytest

# Run with auto-reload
uvicorn app.main:app --reload

# Check code style
flake8 app/
black app/

# Type checking
mypy app/
```

### Frontend Development

```bash
# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm run start

# Lint code
npm run lint

# Type checking
npx tsc --noEmit
```

### Testing

#### Backend Tests
```bash
cd ai-mock-interview-backend
pytest tests/ -v
pytest tests/test_api.py -v
pytest tests/test_ml_service.py -v
```

#### Frontend Tests
```bash
cd ai-mock-interview-frontend
npm test
npm run test:watch
```

## 🚢 Deployment

### Backend Deployment

#### Option 1: Docker
```bash
cd ai-mock-interview-backend
docker build -t ai-interview-backend .
docker run -p 8000:8000 --env-file .env ai-interview-backend
```

#### Option 2: Traditional Hosting
- Deploy to services like Heroku, Railway, or DigitalOcean
- Set environment variables (GOOGLE_API_KEY, VAPI credentials)
- SQLite works for small-scale production
- For larger scale, configure PostgreSQL

### Frontend Deployment

#### Vercel (Recommended)
```bash
cd ai-mock-interview-frontend
vercel deploy
```

**Important**: Configure environment variables in your deployment platform.

## 📝 Environment Variables Summary

### Backend (.env)
- `DATABASE_URL` - Database connection string (SQLite default)
- `GOOGLE_API_KEY` - Google Gemini API key (**required**)
- `VAPI_API_KEY` - VAPI private API key (required for voice)
- `VAPI_WEBHOOK_SECRET` - VAPI webhook secret
- `BACKEND_URL` - Backend URL for webhooks (use ngrok URL in dev)
- `DEBUG` - Debug mode (True/False)

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL (http://localhost:8000)
- `NEXT_PUBLIC_VAPI_PUBLIC_KEY` - VAPI public key (starts with pk_)
- `NEXT_PUBLIC_VAPI_ASSISTANT_ID` - VAPI assistant ID

**📖 See [SETUP.md](./SETUP.md) for detailed configuration guide**

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Google** for Gemini AI models
- **VAPI** for voice integration
- **FastAPI** for the excellent Python web framework
- **Next.js** for the React framework
- **shadcn/ui** for beautiful UI components
- **Monaco Editor** for the VS Code-like code editing experience
- **scikit-learn** for ML capabilities

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

Made with ❤️ for better interview preparation, by CPR.
