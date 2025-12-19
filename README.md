# AI Mock Interview Platform

A full-stack AI-powered mock interview platform featuring voice integration, real-time feedback, and ML-based response analysis. The platform helps users practice interview skills with intelligent feedback and performance metrics.

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
- **Voice-enabled interviews** using VAPI integration
- **AI-powered feedback** using machine learning models
- **Multiple interview types**: Technical (Software, Data Science), Behavioral, and Company-specific
- **Real-time analysis** of responses with scoring and recommendations
- **Comprehensive reporting** with strengths, improvements, and detailed metrics

## ✨ Features

### Frontend (Next.js)
- 🎨 Modern, responsive UI with Tailwind CSS
- 🎙️ Voice interview interface with VAPI integration
- 📊 Real-time performance dashboard
- 📈 Interactive charts and visualizations
- 🎯 Multiple interview types and difficulty levels
- 📱 Mobile-responsive design
- 🌓 Dark mode support

### Backend (FastAPI)
- 🚀 High-performance RESTful API
- 🤖 ML-powered response analysis using scikit-learn
- 📝 Comprehensive question database (50+ questions)
- 🔊 VAPI webhook integration for voice processing
- 💾 Database support (PostgreSQL/SQLite)
- 📊 Advanced analytics and metrics
- 🔐 Secure API endpoints
- 📖 Automatic API documentation (Swagger/ReDoc)

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (React 19)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI, shadcn/ui
- **State Management**: React Hooks
- **Voice Integration**: VAPI SDK
- **Animations**: Framer Motion, React Three Fiber
- **Charts**: Recharts
- **Icons**: Tabler Icons, Heroicons

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Database**: PostgreSQL (production), SQLite (development)
- **ORM**: SQLAlchemy
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
│   │   ├── models.py               # SQLAlchemy database models
│   │   ├── database.py             # Database configuration
│   │   ├── vapi_service.py         # VAPI integration service
│   │   ├── ml_service.py           # ML analysis service
│   │   └── ml/                     # Machine learning modules
│   │       └── feature_extraction.py
│   ├── data/
│   │   ├── interview-questions.json # Question database
│   │   └── training_data.csv       # ML training data
│   ├── scripts/
│   │   ├── generate_training_data.py
│   │   └── train_model.py          # ML model training script
│   ├── tests/                      # Test files
│   ├── logs/                       # Application logs
│   ├── models/                     # Trained ML models
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
- **VAPI Account** and API key ([Get it here](https://vapi.ai))

### Quick Start

#### 1. Clone & Install

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
# Edit .env with your VAPI credentials
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

#### 4. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Environment Variables

**Backend** (`.env`):
```env
VAPI_API_KEY=your_private_key
VAPI_WEBHOOK_SECRET=your_webhook_secret
SECRET_KEY=your_jwt_secret
DATABASE_URL=sqlite:///./interview_platform.db
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
venv\Scripts\activate  # Windows

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
# or
yarn dev
# or
pnpm dev
```

The frontend will be available at: http://localhost:3000

## ⚙️ Configuration

### VAPI Setup

1. Create a VAPI account at [vapi.ai](https://vapi.ai)
2. Create a new assistant for the mock interview
3. Copy your API keys and phone number
4. Add them to your `.env` files

See [VAPI_SETUP_GUIDE.md](./ai-mock-interview-frontend/VAPI_SETUP_GUIDE.md) for detailed setup instructions.

### Database Configuration

**Development**: SQLite (default)
- No additional setup required
- Database file: `interview.db`

**Production**: PostgreSQL
```env
DATABASE_URL=postgresql://user:password@localhost:5432/interview_db
```

### ML Model Training

To retrain the ML models with your own data:

```bash
cd ai-mock-interview-backend
python scripts/generate_training_data.py  # Generate synthetic training data
python scripts/train_model.py             # Train the models
```

Models will be saved to the `models/` directory.

## 📚 API Documentation

### Main Endpoints

#### Start Interview
```http
POST /api/v1/interview/start
Content-Type: application/json

{
  "interview_type": "technical_software",
  "difficulty": "intermediate",
  "duration": 30,
  "company": "Optional Company Name"
}
```

#### Analyze Response
```http
POST /api/v1/interview/analyze-response
Content-Type: application/json

{
  "session_id": "uuid",
  "response_text": "User's answer",
  "question_id": 1,
  "question_number": 1
}
```

#### Get Feedback
```http
GET /api/v1/interview/feedback/{session_id}
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
- Ensure PostgreSQL database is configured
- Set environment variables
- Run migrations: `alembic upgrade head`

### Frontend Deployment

#### Vercel (Recommended)
```bash
cd ai-mock-interview-frontend
vercel deploy
```

#### Other Platforms
- Netlify
- AWS Amplify
- DigitalOcean App Platform

**Important**: Configure environment variables in your deployment platform.

## 📝 Environment Variables Summary

### Backend (.env)
- `DATABASE_URL` - Database connection string
- `VAPI_API_KEY` - VAPI private API key
- `VAPI_PHONE_NUMBER` - VAPI phone number
- `SECRET_KEY` - Application secret key
- `ENVIRONMENT` - development/production

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL` - Backend API URL
- `NEXT_PUBLIC_VAPI_PUBLIC_KEY` - VAPI public key

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **VAPI** for voice integration
- **FastAPI** for the excellent Python web framework
- **Next.js** for the React framework
- **shadcn/ui** for beautiful UI components
- **scikit-learn** for ML capabilities

## 📧 Support

For issues, questions, or contributions, please open an issue on GitHub.

---

Made with ❤️ for better interview preparation, by CPR.
