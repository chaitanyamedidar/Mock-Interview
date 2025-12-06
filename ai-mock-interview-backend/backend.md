# models.py

from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, Boolean, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model (optional - for authentication)"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    last_login = Column(TIMESTAMP, nullable=True)

class InterviewSession(Base):
    """Interview session model"""
    __tablename__ = 'interview_sessions'
    
    session_id = Column(String(36), primary_key=True)
    user_id = Column(Integer, nullable=True)
    interview_type = Column(String(50), nullable=False)
    difficulty_level = Column(String(20), nullable=False)
    company = Column(String(100), nullable=True)
    duration_minutes = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False)  # in_progress, completed, abandoned
    started_at = Column(TIMESTAMP, server_default=func.now())
    completed_at = Column(TIMESTAMP, nullable=True)
    overall_score = Column(DECIMAL(4, 2), nullable=True)
    overall_rating = Column(String(20), nullable=True)

class InterviewQuestion(Base):
    """Interview questions model"""
    __tablename__ = 'interview_questions'
    
    question_id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    interview_type = Column(String(50), nullable=False)
    difficulty_level = Column(String(20), nullable=False)
    company = Column(String(100), nullable=True)
    category = Column(String(50), nullable=True)
    expected_keywords = Column(ARRAY(Text), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

class SessionResponse(Base):
    """User responses to interview questions"""
    __tablename__ = 'session_responses'
    
    response_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), nullable=False)
    question_id = Column(Integer, nullable=False)
    question_number = Column(Integer, nullable=False)
    response_text = Column(Text, nullable=False)
    response_audio_url = Column(String(500), nullable=True)
    timestamp = Column(TIMESTAMP, server_default=func.now())
    
    # Analysis metrics
    word_count = Column(Integer, nullable=True)
    filler_word_count = Column(Integer, nullable=True)
    technical_term_count = Column(Integer, nullable=True)
    average_word_length = Column(DECIMAL(5, 2), nullable=True)
    speaking_pace = Column(Integer, nullable=True)
    
    # ML Model scores
    content_quality_score = Column(DECIMAL(4, 2), nullable=True)
    communication_score = Column(DECIMAL(4, 2), nullable=True)
    confidence_score = Column(DECIMAL(4, 2), nullable=True)
    technical_accuracy_score = Column(DECIMAL(4, 2), nullable=True)
    overall_response_score = Column(DECIMAL(4, 2), nullable=True)
    response_rating = Column(String(20), nullable=True)

class FeedbackDetail(Base):
    """Detailed feedback for responses"""
    __tablename__ = 'feedback_details'
    
    feedback_id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), nullable=False)
    response_id = Column(Integer, nullable=True)
    feedback_type = Column(String(50), nullable=False)
    feedback_text = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

class MLTrainingData(Base):
    """Store data for continuous ML model improvement"""
    __tablename__ = 'ml_training_data'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_text = Column(Text, nullable=False)
    response_text = Column(Text, nullable=False)
    manual_label = Column(String(20), nullable=True)
    features = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    is_validated = Column(Boolean, default=False)
```

---

## Database Configuration

```python
# database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./interview_platform.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv('DEBUG') == 'True' else False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

def get_db():
    """
    Dependency for FastAPI to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    Initialize database and create tables
    """
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

def seed_questions():
    """
    Seed database with sample interview questions
    """
    from models import InterviewQuestion
    
    db = SessionLocal()
    
    # Technical Software Engineering Questions
    technical_questions = [
        {
            'question_text': 'Explain the difference between REST and GraphQL APIs',
            'interview_type': 'technical_software',
            'difficulty_level': 'intermediate',
            'category': 'API Design',
            'expected_keywords': ['REST', 'GraphQL', 'HTTP', 'query', 'endpoint']
        },
        {
            'question_text': 'What is the time complexity of binary search and explain how it works?',
            'interview_type': 'technical_software',
            'difficulty_level': 'entry',
            'category': 'Algorithms',
            'expected_keywords': ['O(log n)', 'divide', 'conquer', 'sorted', 'array']
        },
        {
            'question_text': 'Describe how you would design a URL shortener like bit.ly',
            'interview_type': 'technical_software',
            'difficulty_level': 'advanced',
            'category': 'System Design',
            'expected_keywords': ['hashing', 'database', 'scalability', 'redirect', 'unique']
        },
        {
            'question_text': 'Explain the concept of database indexing and when you would use it',
            'interview_type': 'technical_software',
            'difficulty_level': 'intermediate',
            'category': 'Databases',
            'expected_keywords': ['B-tree', 'performance', 'query', 'primary key', 'foreign key']
        },
        {
            'question_text': 'What are the SOLID principles in object-oriented programming?',
            'interview_type': 'technical_software',
            'difficulty_level': 'intermediate',
            'category': 'OOP',
            'expected_keywords': ['single responsibility', 'open-closed', 'liskov', 'interface', 'dependency']
        },
    ]
    
    # Behavioral Questions
    behavioral_questions = [
        {
            'question_text': 'Tell me about a time you faced a difficult technical challenge and how you overcame it',
            'interview_type': 'behavioral',
            'difficulty_level': 'intermediate',
            'category': 'Problem Solving',
            'expected_keywords': ['challenge', 'approach', 'solution', 'result', 'learned']
        },
        {
            'question_text': 'Describe a situation where you had to work with a difficult team member',
            'interview_type': 'behavioral',
            'difficulty_level': 'intermediate',
            'category': 'Teamwork',
            'expected_keywords': ['communication', 'conflict', 'resolution', 'collaboration', 'outcome']
        },
        {
            'question_text': 'What is your greatest professional achievement to date?',
            'interview_type': 'behavioral',
            'difficulty_level': 'entry',
            'category': 'Achievements',
            'expected_keywords': ['project', 'impact', 'role', 'success', 'proud']
        },
    ]
    
    # Company-specific questions (Google)
    google_questions = [
        {
            'question_text': 'How would you find the kth largest element in an unsorted array?',
            'interview_type': 'technical_software',
            'difficulty_level': 'advanced',
            'category': 'Algorithms',
            'company': 'google',
            'expected_keywords': ['quickselect', 'heap', 'partition', 'O(n)', 'average']
        },
        {
            'question_text': 'Design a recommendation system for YouTube videos',
            'interview_type': 'technical_software',
            'difficulty_level': 'advanced',
            'category': 'System Design',
            'company': 'google',
            'expected_keywords': ['collaborative filtering', 'machine learning', 'scalability', 'personalization']
        },
    ]
    
    # Combine all questions
    all_questions = technical_questions + behavioral_questions + google_questions
    
    # Add to database
    for q_data in all_questions:
        question = InterviewQuestion(**q_data)
        db.add(question)
    
    db.commit()
    db.close()
    print(f"Seeded {len(all_questions)} questions successfully")

if __name__ == '__main__':
    init_database()
    seed_questions()
```

---

## Environment Variables Configuration

```bash
# .env file

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/interview_db
# For development, use SQLite:
# DATABASE_URL=sqlite:///./interview_platform.db

# VAPI Configuration
VAPI_API_KEY=your_vapi_api_key_here
VAPI_WEBHOOK_SECRET=your_webhook_secret_here

# Backend URL (for VAPI webhooks)
BACKEND_URL=https://your-backend-domain.com

# OpenAI (if using directly)
OPENAI_API_KEY=your_openai_key_here

# Application Settings
DEBUG=True
SECRET_KEY=your_secret_key_for_jwt

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.com
```

---

## Requirements File

```txt
# requirements.txt

# Web Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9  # PostgreSQL
alembic==1.12.1  # Database migrations

# Machine Learning
scikit-learn==1.3.2
pandas==2.1.3
numpy==1.26.2
joblib==1.3.2

# NLP
nltk==3.8.1
spacy==3.7.2

# API & HTTP
requests==2.31.0
httpx==0.25.2

# Environment & Configuration
python-dotenv==1.0.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Authentication (optional)
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4

# CORS
python-cors==1.0.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1

# Utilities
python-dateutil==2.8.2
pytz==2023.3
```

---

## Project Structure

```
interview-platform/
│
├── backend/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── database.py             # Database configuration
│   ├── models.py               # SQLAlchemy models
│   ├── ml_service.py           # ML analysis service
│   ├── vapi_service.py         # VAPI integration
│   ├── feature_extraction.py  # Feature engineering
│   ├── model_training.py       # ML model training
│   │
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── interview.py        # Interview routes
│   │   ├── feedback.py         # Feedback routes
│   │   ├── questions.py        # Questions routes
│   │   └── vapi_webhook.py     # VAPI webhook handler
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── interview.py        # Pydantic schemas
│   │   └── feedback.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── auth.py             # Authentication utilities
│       └── helpers.py          # Helper functions
│
├── models/
│   ├── interview_classifier.pkl  # Trained ML model
│   └── tfidf_vectorizer.pkl      # Vectorizer
│
├── data/
│   ├── training_data.csv       # Training dataset
│   └── questions_seed.json     # Seed questions
│
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_ml_service.py
│   └── test_database.py
│
├── .env                        # Environment variables
├── .gitignore
├── requirements.txt
├── README.md
└── alembic.ini                 # Database migrations config
```

---

## API Endpoints Summary

### Interview Management
- `POST /api/interview/start` - Start new interview session
- `POST /api/interview/analyze-response` - Analyze single response
- `POST /api/interview/end` - End interview and get feedback
- `GET /api/interview/session/{session_id}` - Get session details

### Questions
- `GET /api/questions/{interview_type}` - Get questions by type
- `GET /api/questions/random` - Get random questions
- `POST /api/questions/add` - Add new question (admin)

### Feedback
- `GET /api/feedback/{session_id}` - Get detailed feedback
- `GET /api/feedback/{session_id}/pdf` - Download feedback as PDF

### VAPI Webhooks
- `POST /api/vapi/webhook` - Handle VAPI callbacks
- `POST /api/vapi/transcript` - Process transcripts

### Analytics (Optional)
- `GET /api/analytics/user/{user_id}` - User progress analytics
- `GET /api/analytics/trends` - Overall trends

---

## Testing Strategy

```python
# tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_start_interview():
    """Test starting a new interview"""
    response = client.post("/api/interview/start", json={
        "interview_type": "technical_software",
        "difficulty": "intermediate",
        "duration": 20
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert len(data["questions"]) > 0

def test_analyze_response():
    """Test response analysis"""
    # First start an interview
    start_response = client.post("/api/interview/start", json={
        "interview_type": "technical_software",
        "difficulty": "intermediate",
        "duration": 10
    })
    session_id = start_response.json()["session_id"]
    question_id = start_response.json()["questions"][0]["question_id"]
    
    # Analyze a response
    response = client.post("/api/interview/analyze-response", json={
        "session_id": session_id,
        "response_text": "REST API is an architectural style that uses HTTP methods...",
        "question_id": question_id,
        "question_number": 1
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "quality_score" in data
    assert "rating" in data
    assert data["quality_score"] >= 0 and data["quality_score"] <= 10

def test_end_interview():
    """Test ending interview and getting feedback"""
    # Start and complete mock interview
    start_response = client.post("/api/interview/start", json={
        "interview_type": "behavioral",
        "difficulty": "intermediate",
        "duration": 10
    })
    session_id = start_response.json()["session_id"]
    
    # End interview
    response = client.post("/api/interview/end", json={
        "session_id": session_id,
        "responses": []
    })
    
    assert response.status_code == 200
    data = response.json()
    assert "overall_score" in data
    assert "strengths" in data
    assert "improvements" in data
```

---

## Deployment Guide

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/yourusername/interview-platform.git
cd interview-platform

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Initialize database
python backend/database.py

# 6. Train ML model (first time only)
python backend/model_training.py

# 7. Run development server
uvicorn backend.main:app --reload --port 8000

# Server will be available at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### Production Deployment (Docker)

```dockerfile
# Dockerfile

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -m nltk.downloader punkt stopwords

# Copy application code
COPY backend/ ./backend/
COPY models/ ./models/

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml

version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: interview_db
      POSTGRES_USER: interview_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: .
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://interview_user:secure_password@db:5432/interview_db
      VAPI_API_KEY: ${VAPI_API_KEY}
      BACKEND_URL: ${BACKEND_URL}
    depends_on:
      - db
    volumes:
      - ./models:/app/models

volumes:
  postgres_data:
```

### Deploy to Cloud

**Heroku:**
```bash
# 1. Create Heroku app
heroku create interview-platform-api

# 2. Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# 3. Set environment variables
heroku config:set VAPI_API_KEY=your_key
heroku config:set BACKEND_URL=https://interview-platform-api.herokuapp.com

# 4. Deploy
git push heroku main

# 5. Initialize database
heroku run python backend/database.py
```

**AWS EC2/EB:**
```bash
# Use AWS Elastic Beanstalk CLI
eb init -p python-3.11 interview-platform
eb create interview-platform-env
eb deploy
```

---

## Monitoring & Logging

```python
# logging_config.py

import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logging():
    """
    Configure application logging
    """
    # Create logger
    logger = logging.getLogger("interview_platform")
    logger.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_format)
    
    # File handler
    file_handler = RotatingFileHandler(
        'logs/application.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(console_format)
    
    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger

# Usage in main.py
from logging_config import setup_logging

logger = setup_logging()

@app.middleware("http")
async def log_requests(request, call_next):
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response
```

---

## Security Considerations

1. **API Key Protection:**
   - Never commit .env files
   - Use environment variables
   - Rotate keys regularly

2. **Input Validation:**
   - Use Pydantic models for validation
   - Sanitize user inputs
   - Implement rate limiting

3. **Database Security:**
   - Use parameterized queries (SQLAlchemy ORM)
   - Implement proper access controls
   - Regular backups

4. **CORS Configuration:**
   - Specify exact origins in production
   - Don't use wildcard (*) in production

5. **Authentication (if implementing):**
   - Use JWT tokens
   - Implement refresh tokens
   - Hash passwords with bcrypt

---

## Performance Optimization

1. **Database:**
   - Add indexes on frequently queried columns
   - Use connection pooling
   - Implement caching (Redis)

2. **ML Model:**
   - Load model once at startup
   - Use batch predictions when possible
   - Consider model quantization

3. **API:**
   - Implement response caching
   - Use async/await for I/O operations
   - Add CDN for static assets

4. **Monitoring:**
   - Set up APM (Application Performance Monitoring)
   - Track API response times
   - Monitor database query performance

---

## Next Steps & Future Enhancements

1. **Advanced ML Features:**
   - Speech emotion detection
   - Pace and tone analysis
   - Real-time suggestions during interview

2. **Additional Features:**
   - Video recording option
   - Interview replay
   - Progress tracking over time
   - Peer comparison anonymized

3. **Analytics Dashboard:**
   - Admin panel for question management
   - User analytics and trends
   - ML model performance tracking

4. **Integrations:**
   - Calendar integration for scheduled practice
   - LinkedIn integration
   - Export to resume builders

---

## Documentation & Handoff

When handing off to a developer, provide:

1. **API Documentation**: Auto-generated at `/docs` (FastAPI Swagger)
2. **Database Schema**: ERD diagram
3. **ML Model Documentation**: Training process, features, performance metrics
4. **Deployment Guide**: Step-by-step deployment instructions
5. **Testing Suite**: Comprehensive test coverage
6. **Maintenance Guide**: How to retrain model, update questions, etc.

---

## Troubleshooting Common Issues

### Issue: ML Model Not Loading
**Solution:** Ensure model file exists in `models/` directory and path is correct

### Issue: Database Connection Error
**Solution:** Check DATABASE_URL in .env, ensure PostgreSQL is running

### Issue: VAPI Webhook Not Working
**Solution:** Verify webhook URL is publicly accessible, check VAPI_WEBHOOK_SECRET

### Issue: Poor ML Predictions
**Solution:** Retrain model with more diverse data, adjust feature engineering

---

This comprehensive prompt covers everything needed to build a production-ready backend for your AI mock interview platform!# Complete Backend & Functionality Development Prompt for AI Mock Interview Platform

## Project Overview
Build a complete backend system for an AI-powered mock interview platform that integrates with VAPI voice assistant, includes a trained ML model for response analysis, and provides comprehensive feedback to users. The system should handle interview sessions, analyze responses in real-time, store data, and generate detailed feedback reports.

---

## Technology Stack

### Backend Framework
- **Python Flask** or **FastAPI** (recommend FastAPI for better async support and automatic API documentation)
- **Python 3.9+**

### Database
- **PostgreSQL** (primary database for production)
- **SQLite** (for development/testing)
- Use **SQLAlchemy** ORM for database operations

### Machine Learning
- **scikit-learn** for ML models (classification, feature extraction)
- **NLTK** or **spaCy** for NLP tasks
- **pandas** for data processing
- **numpy** for numerical operations
- **pickle** for model serialization

### APIs & Integrations
- **VAPI SDK** for voice assistant integration
- **OpenAI API** (optional, for enhanced analysis)
- **RESTful API** design for frontend communication

### Additional Libraries
- **python-dotenv** for environment variables
- **CORS** middleware for cross-origin requests
- **JWT** for authentication (optional but recommended)
- **pydantic** for data validation
- **pytest** for testing

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React/HTML)                 │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/WebSocket
┌─────────────────────▼───────────────────────────────────┐
│                  API Gateway (FastAPI)                   │
│  ┌─────────────┬──────────────┬─────────────────────┐   │
│  │   Auth      │   Interview  │    Feedback         │   │
│  │   Routes    │   Routes     │    Routes           │   │
│  └─────────────┴──────────────┴─────────────────────┘   │
└───────┬──────────────┬────────────────┬────────────────┘
        │              │                │
┌───────▼─────┐ ┌─────▼──────┐  ┌─────▼──────────────┐
│   Database  │ │   VAPI     │  │  ML Model Engine   │
│ (PostgreSQL)│ │   Service  │  │  (scikit-learn)    │
└─────────────┘ └────────────┘  └────────────────────┘
```

---

## Database Schema Design

### Tables Structure

#### 1. **users** (Optional - if implementing authentication)
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);
```

#### 2. **interview_sessions**
```sql
CREATE TABLE interview_sessions (
    session_id VARCHAR(36) PRIMARY KEY,  -- UUID
    user_id INTEGER REFERENCES users(id),  -- NULL if no auth
    interview_type VARCHAR(50) NOT NULL,  -- 'technical_software', 'behavioral', etc.
    difficulty_level VARCHAR(20) NOT NULL,  -- 'entry', 'intermediate', 'advanced'
    company VARCHAR(100),  -- 'google', 'amazon', NULL for generic
    duration_minutes INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,  -- 'in_progress', 'completed', 'abandoned'
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    overall_score DECIMAL(4,2),  -- 0.00 to 10.00
    overall_rating VARCHAR(20)  -- 'excellent', 'good', 'average', 'poor'
);
```

#### 3. **interview_questions**
```sql
CREATE TABLE interview_questions (
    question_id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    interview_type VARCHAR(50) NOT NULL,
    difficulty_level VARCHAR(20) NOT NULL,
    company VARCHAR(100),  -- NULL for generic
    category VARCHAR(50),  -- 'algorithms', 'system_design', 'behavioral'
    expected_keywords TEXT[],  -- Array of keywords
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. **session_responses**
```sql
CREATE TABLE session_responses (
    response_id SERIAL PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES interview_sessions(session_id),
    question_id INTEGER REFERENCES interview_questions(question_id),
    question_number INTEGER NOT NULL,
    response_text TEXT NOT NULL,
    response_audio_url VARCHAR(500),  -- Optional: store audio files
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Analysis metrics
    word_count INTEGER,
    filler_word_count INTEGER,
    technical_term_count INTEGER,
    average_word_length DECIMAL(5,2),
    speaking_pace INTEGER,  -- words per minute
    
    -- ML Model scores
    content_quality_score DECIMAL(4,2),
    communication_score DECIMAL(4,2),
    confidence_score DECIMAL(4,2),
    technical_accuracy_score DECIMAL(4,2),
    overall_response_score DECIMAL(4,2),
    response_rating VARCHAR(20)  -- 'excellent', 'good', 'average', 'poor'
);
```

#### 5. **feedback_details**
```sql
CREATE TABLE feedback_details (
    feedback_id SERIAL PRIMARY KEY,
    session_id VARCHAR(36) REFERENCES interview_sessions(session_id),
    response_id INTEGER REFERENCES session_responses(response_id),
    feedback_type VARCHAR(50),  -- 'strength', 'improvement', 'suggestion'
    feedback_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 6. **ml_training_data** (for continuous improvement)
```sql
CREATE TABLE ml_training_data (
    id SERIAL PRIMARY KEY,
    question_text TEXT NOT NULL,
    response_text TEXT NOT NULL,
    manual_label VARCHAR(20),  -- Human-verified label
    features JSONB,  -- Store extracted features
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_validated BOOLEAN DEFAULT FALSE
);
```

---

## Machine Learning Model Development

### Dataset Creation and Preparation

#### Step 1: Generate Training Dataset
```python
# dataset_generator.py

import pandas as pd
import random

# Sample questions by category
TECHNICAL_QUESTIONS = [
    "Explain the difference between REST and GraphQL APIs",
    "What is the time complexity of binary search?",
    "Describe how you would design a URL shortener",
    "Explain the concept of database indexing",
    "What are the SOLID principles in OOP?",
    # Add 50+ more
]

BEHAVIORAL_QUESTIONS = [
    "Tell me about a time you faced a difficult challenge",
    "Describe a situation where you disagreed with a team member",
    "What's your greatest professional achievement?",
    # Add 50+ more
]

# Sample responses with varying quality
def generate_sample_responses():
    """
    Generate synthetic training data with labeled quality
    """
    training_data = []
    
    # Excellent responses (score 9-10)
    excellent_patterns = [
        "structured detailed answer with examples",
        "uses technical terminology correctly",
        "provides context and specific metrics",
        "clear beginning, middle, and end"
    ]
    
    # Poor responses (score 1-4)
    poor_patterns = [
        "um... I think... like... you know...",
        "very short incomplete answer",
        "completely off-topic response",
        "no technical depth"
    ]
    
    # Generate 1000+ labeled examples
    for question in TECHNICAL_QUESTIONS:
        # Excellent example
        training_data.append({
            'question': question,
            'response': generate_excellent_response(question),
            'content_quality': 9,
            'communication': 9,
            'confidence': 9,
            'technical_accuracy': 9,
            'overall_rating': 'excellent'
        })
        
        # Good example
        training_data.append({
            'question': question,
            'response': generate_good_response(question),
            'content_quality': 7,
            'communication': 7,
            'confidence': 7,
            'technical_accuracy': 7,
            'overall_rating': 'good'
        })
        
        # Average example
        training_data.append({
            'question': question,
            'response': generate_average_response(question),
            'content_quality': 5,
            'communication': 5,
            'confidence': 5,
            'technical_accuracy': 5,
            'overall_rating': 'average'
        })
        
        # Poor example
        training_data.append({
            'question': question,
            'response': generate_poor_response(question),
            'content_quality': 3,
            'communication': 3,
            'confidence': 3,
            'technical_accuracy': 3,
            'overall_rating': 'poor'
        })
    
    return pd.DataFrame(training_data)

# Save to CSV
df = generate_sample_responses()
df.to_csv('training_data.csv', index=False)
```

#### Step 2: Feature Engineering
```python
# feature_extraction.py

import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')

class ResponseFeatureExtractor:
    """
    Extract comprehensive features from interview responses
    """
    
    def __init__(self):
        self.filler_words = [
            'um', 'uh', 'like', 'you know', 'actually', 
            'basically', 'literally', 'sort of', 'kind of'
        ]
        
        self.technical_terms = {
            'software': ['api', 'algorithm', 'database', 'function', 'class', 
                        'object', 'array', 'hash', 'tree', 'graph', 'stack',
                        'queue', 'complexity', 'optimization', 'scalability'],
            'data_science': ['model', 'training', 'dataset', 'feature', 
                           'regression', 'classification', 'neural', 'accuracy',
                           'precision', 'recall', 'overfitting'],
            'system_design': ['load balancer', 'cache', 'database', 'microservices',
                            'api gateway', 'cdn', 'replication', 'sharding']
        }
        
        self.confidence_indicators = {
            'positive': ['definitely', 'certainly', 'confident', 'sure', 'absolutely'],
            'negative': ['maybe', 'perhaps', 'not sure', 'think', 'guess', 'probably']
        }
    
    def extract_all_features(self, response_text, question_text='', interview_type='technical'):
        """
        Extract all features from a response
        Returns: dict of features
        """
        features = {}
        
        # Basic text statistics
        features.update(self._extract_basic_stats(response_text))
        
        # Filler words analysis
        features.update(self._analyze_filler_words(response_text))
        
        # Technical terminology
        features.update(self._analyze_technical_terms(response_text, interview_type))
        
        # Sentence structure
        features.update(self._analyze_sentence_structure(response_text))
        
        # Confidence indicators
        features.update(self._analyze_confidence(response_text))
        
        # Relevance to question
        if question_text:
            features.update(self._analyze_relevance(response_text, question_text))
        
        return features
    
    def _extract_basic_stats(self, text):
        """Basic statistical features"""
        words = word_tokenize(text.lower())
        sentences = sent_tokenize(text)
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': np.mean([len(w) for w in words]) if words else 0,
            'avg_sentence_length': len(words) / len(sentences) if sentences else 0,
            'character_count': len(text),
            'unique_word_ratio': len(set(words)) / len(words) if words else 0
        }
    
    def _analyze_filler_words(self, text):
        """Count filler words"""
        text_lower = text.lower()
        filler_count = sum(text_lower.count(word) for word in self.filler_words)
        words = word_tokenize(text_lower)
        
        return {
            'filler_word_count': filler_count,
            'filler_word_ratio': filler_count / len(words) if words else 0
        }
    
    def _analyze_technical_terms(self, text, interview_type):
        """Count technical terms based on interview type"""
        text_lower = text.lower()
        terms = self.technical_terms.get(interview_type, self.technical_terms['software'])
        
        tech_count = sum(text_lower.count(term) for term in terms)
        words = word_tokenize(text_lower)
        
        return {
            'technical_term_count': tech_count,
            'technical_term_ratio': tech_count / len(words) if words else 0
        }
    
    def _analyze_sentence_structure(self, text):
        """Analyze sentence complexity"""
        sentences = sent_tokenize(text)
        
        if not sentences:
            return {
                'has_structure': False,
                'starts_with_context': False,
                'has_examples': False
            }
        
        # Check for structured response
        has_structure = len(sentences) >= 3
        
        # Check if starts with context (first sentence > 10 words)
        first_sentence_words = word_tokenize(sentences[0])
        starts_with_context = len(first_sentence_words) > 10
        
        # Check for examples (keywords: "example", "for instance", "such as")
        example_keywords = ['example', 'for instance', 'such as', 'like when', 'for example']
        has_examples = any(keyword in text.lower() for keyword in example_keywords)
        
        return {
            'has_structure': has_structure,
            'starts_with_context': starts_with_context,
            'has_examples': has_examples
        }
    
    def _analyze_confidence(self, text):
        """Analyze confidence level in response"""
        text_lower = text.lower()
        
        positive_count = sum(text_lower.count(word) for word in self.confidence_indicators['positive'])
        negative_count = sum(text_lower.count(word) for word in self.confidence_indicators['negative'])
        
        confidence_score = positive_count - negative_count
        
        return {
            'confidence_indicators_positive': positive_count,
            'confidence_indicators_negative': negative_count,
            'confidence_score': confidence_score
        }
    
    def _analyze_relevance(self, response_text, question_text):
        """Calculate relevance between question and response"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity
        
        vectorizer = TfidfVectorizer()
        try:
            tfidf_matrix = vectorizer.fit_transform([question_text, response_text])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            similarity = 0.0
        
        return {
            'relevance_score': similarity
        }

# Usage example
extractor = ResponseFeatureExtractor()
features = extractor.extract_all_features(
    "REST API is an architectural style...",
    "Explain REST API",
    "technical_software"
)
```

#### Step 3: Model Training
```python
# model_training.py

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import pickle
import joblib

class InterviewResponseClassifier:
    """
    Train ML model to classify interview response quality
    """
    
    def __init__(self):
        self.feature_extractor = ResponseFeatureExtractor()
        self.scaler = StandardScaler()
        self.model = None
        self.feature_names = None
    
    def prepare_training_data(self, csv_path):
        """
        Load and prepare training data
        """
        df = pd.read_csv(csv_path)
        
        # Extract features for each response
        print("Extracting features from training data...")
        feature_list = []
        
        for idx, row in df.iterrows():
            features = self.feature_extractor.extract_all_features(
                row['response'],
                row['question'],
                row.get('interview_type', 'technical_software')
            )
            feature_list.append(features)
            
            if idx % 100 == 0:
                print(f"Processed {idx}/{len(df)} samples")
        
        # Convert to DataFrame
        X = pd.DataFrame(feature_list)
        y = df['overall_rating']  # Target variable
        
        self.feature_names = X.columns.tolist()
        
        return X, y
    
    def train_model(self, X, y, test_size=0.2):
        """
        Train the classification model
        """
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Try multiple models and select best
        models = {
            'RandomForest': RandomForestClassifier(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                class_weight='balanced'
            ),
            'GradientBoosting': GradientBoostingClassifier(
                n_estimators=200,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
        }
        
        best_score = 0
        best_model_name = None
        
        print("\nTraining and evaluating models...")
        for name, model in models.items():
            # Train
            model.fit(X_train_scaled, y_train)
            
            # Cross-validation score
            cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
            mean_cv_score = cv_scores.mean()
            
            # Test score
            test_score = model.score(X_test_scaled, y_test)
            
            print(f"\n{name}:")
            print(f"  CV Score: {mean_cv_score:.4f} (+/- {cv_scores.std():.4f})")
            print(f"  Test Score: {test_score:.4f}")
            
            if mean_cv_score > best_score:
                best_score = mean_cv_score
                best_model_name = name
                self.model = model
        
        print(f"\nBest model: {best_model_name}")
        
        # Detailed evaluation on best model
        y_pred = self.model.predict(X_test_scaled)
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        print("\nConfusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Feature importance
        if hasattr(self.model, 'feature_importances_'):
            feature_importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print("\nTop 10 Most Important Features:")
            print(feature_importance.head(10))
        
        return X_test_scaled, y_test, y_pred
    
    def save_model(self, filepath='models/interview_classifier.pkl'):
        """
        Save trained model and scaler
        """
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'feature_extractor': self.feature_extractor
        }
        
        joblib.dump(model_data, filepath)
        print(f"\nModel saved to {filepath}")
    
    def load_model(self, filepath='models/interview_classifier.pkl'):
        """
        Load trained model
        """
        model_data = joblib.load(filepath)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_names = model_data['feature_names']
        self.feature_extractor = model_data['feature_extractor']
        print(f"Model loaded from {filepath}")
    
    def predict(self, response_text, question_text='', interview_type='technical_software'):
        """
        Predict quality of a single response
        """
        # Extract features
        features = self.feature_extractor.extract_all_features(
            response_text, question_text, interview_type
        )
        
        # Convert to DataFrame with correct feature order
        X = pd.DataFrame([features])[self.feature_names]
        
        # Scale
        X_scaled = self.scaler.transform(X)
        
        # Predict
        prediction = self.model.predict(X_scaled)[0]
        probabilities = self.model.predict_proba(X_scaled)[0]
        confidence = max(probabilities)
        
        return {
            'prediction': prediction,
            'confidence': confidence,
            'probabilities': dict(zip(self.model.classes_, probabilities)),
            'features': features
        }

# Training script
if __name__ == '__main__':
    # Initialize classifier
    classifier = InterviewResponseClassifier()
    
    # Prepare data
    X, y = classifier.prepare_training_data('training_data.csv')
    
    # Train model
    classifier.train_model(X, y)
    
    # Save model
    classifier.save_model('models/interview_classifier.pkl')
    
    # Test prediction
    test_response = "REST API is an architectural style that uses HTTP methods..."
    result = classifier.predict(test_response, "Explain REST API")
    print(f"\nTest Prediction: {result}")
```

---

## Backend API Implementation

### Main Application Structure

```python
# main.py (FastAPI Application)

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio

# Import custom modules
from database import get_db, SessionLocal
from models import InterviewSession, SessionResponse, FeedbackDetail
from ml_service import InterviewAnalyzer
from vapi_service import VAPIManager

# Initialize FastAPI app
app = FastAPI(
    title="AI Mock Interview API",
    description="Backend API for AI-powered mock interview platform",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = InterviewAnalyzer()
vapi_manager = VAPIManager()

# Pydantic models for request/response
class InterviewStartRequest(BaseModel):
    interview_type: str = Field(..., description="Type of interview")
    difficulty: str = Field(..., description="Difficulty level")
    duration: int = Field(..., description="Duration in minutes")
    company: Optional[str] = None

class InterviewStartResponse(BaseModel):
    session_id: str
    questions: List[Dict[str, Any]]
    vapi_config: Dict[str, Any]

class ResponseAnalysisRequest(BaseModel):
    session_id: str
    response_text: str
    question_id: int
    question_number: int

class ResponseAnalysisResult(BaseModel):
    response_id: int
    quality_score: float
    content_quality: float
    communication: float
    confidence: float
    technical_accuracy: float
    rating: str
    feedback: List[str]
    metrics: Dict[str, Any]

class EndInterviewRequest(BaseModel):
    session_id: str
    responses: List[Dict[str, Any]]

class FeedbackResponse(BaseModel):
    session_id: str
    overall_score: float
    overall_rating: str
    strengths: List[str]
    improvements: List[str]
    detailed_analysis: Dict[str, Any]
    question_breakdown: List[Dict[str, Any]]

# API Routes

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AI Mock Interview API",
        "version": "1.0.0"
    }

@app.post("/api/interview/start", response_model=InterviewStartResponse)
async def start_interview(request: InterviewStartRequest, db: SessionLocal = Depends(get_db)):
    """
    Start a new interview session
    """
    try:
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        # Get questions based on filters
        questions = get_questions_for_interview(
            interview_type=request.interview_type,
            difficulty=request.difficulty,
            company=request.company,
            duration=request.duration,
            db=db
        )
        
        # Create session in database
        session = InterviewSession(
            session_id=session_id,
            interview_type=request.interview_type,
            difficulty_level=request.difficulty,
            company=request.company,
            duration_minutes=request.duration,
            status='in_progress'
        )
        db.add(session)
        db.commit()
        
        # Configure VAPI assistant
        vapi_config = vapi_manager.create_assistant_config(
            session_id=session_id,
            interview_type=request.interview_type,
            questions=[q['question_text'] for q in questions]
        )
        
        return InterviewStartResponse(
            session_id=session_id,
            questions=questions,
            vapi_config=vapi_config
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/analyze-response", response_model=ResponseAnalysisResult)
async def analyze_response(request: ResponseAnalysisRequest, db: SessionLocal = Depends(get_db)):
    """
    Analyze a single interview response using ML model
    """
    try:
        # Get question details
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.question_id == request.question_id
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Get session details
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Analyze response using ML model
        analysis = analyzer.analyze_response(
            response_text=request.response_text,
            question_text=question.question_text,
            interview_type=session.interview_type
        )
        
        # Store response in database
        response_record = SessionResponse(
            session_id=request.session_id,
            question_id=request.question_id,
            question_number=request.question_number,
            response_text=request.response_text,
            word_count=analysis['features']['word_count'],
            filler_word_count=analysis['features']['filler_word_count'],
            technical_term_count=analysis['features']['technical_term_count'],
            average_word_length=analysis['features']['avg_word_length'],
            content_quality_score=analysis['scores']['content_quality'],
            communication_score=analysis['scores']['communication'],
            confidence_score=analysis['scores']['confidence'],
            technical_accuracy_score=analysis['scores']['technical_accuracy'],
            overall_response_score=analysis['overall_score'],
            response_rating=analysis['rating']
        )
        db.add(response_record)
        db.commit()
        db.refresh(response_record)
        
        # Generate and store feedback
        feedback_items = generate_response_feedback(analysis)
        for feedback_text, feedback_type in feedback_items:
            feedback = FeedbackDetail(
                session_id=request.session_id,
                response_id=response_record.response_id,
                feedback_type=feedback_type,
                feedback_text=feedback_text
            )
            db.add(feedback)
        db.commit()
        
        return ResponseAnalysisResult(
            response_id=response_record.response_id,
            quality_score=analysis['overall_score'],
            content_quality=analysis['scores']['content_quality'],
            communication=analysis['scores']['communication'],
            confidence=analysis['scores']['confidence'],
            technical_accuracy=analysis['scores']['technical_accuracy'],
            rating=analysis['rating'],
            feedback=[f[0] for f in feedback_items],
            metrics=analysis['features']
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/end", response_model=FeedbackResponse)
async def end_interview(request: EndInterviewRequest, db: SessionLocal = Depends(get_db)):
    """
    End interview session and generate comprehensive feedback
    """
    try:
        # Get session
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all responses for this session
        responses = db.query(SessionResponse).filter(
            SessionResponse.session_id == request.session_id
        ).all()
        
        # Calculate overall metrics
        overall_analysis = calculate_overall_feedback(responses, db)
        
        # Update session
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        session.overall_score = overall_analysis['overall_score']
        session.overall_rating = overall_analysis['overall_rating']
        db.commit()
        
        # Generate detailed breakdown
        question_breakdown = []
        for response in responses:
            feedback = db.query(FeedbackDetail).filter(
                FeedbackDetail.response_id == response.response_id
            ).all()
            
            question_breakdown.append({
                'question_number': response.question_number,
                'question_id': response.question_id,
                'response_text': response.response_text,
                'scores': {
                    'content_quality': response.content_quality_score,
                    'communication': response.communication_score,
                    'confidence': response.confidence_score,
                    'technical_accuracy': response.technical_accuracy_score,
                    'overall': response.overall_response_score
                },
                'rating': response.response_rating,
                'feedback': [f.feedback_text for f in feedback],
                'metrics': {
                    'word_count': response.word_count,
                    'filler_words': response.filler_word_count,
                    'technical_terms': response.technical_term_count
                }
            })
        
        return FeedbackResponse(
            session_id=request.session_id,
            overall_score=overall_analysis['overall_score'],
            overall_rating=overall_analysis['overall_rating'],
            strengths=overall_analysis['strengths'],
            improvements=overall_analysis['improvements'],
            detailed_analysis=overall_analysis['detailed_metrics'],
            question_breakdown=question_breakdown
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/questions/{interview_type}")
async def get_questions(interview_type: str, difficulty: Optional[str] = None, db: SessionLocal = Depends(get_db)):
    """
    Get available questions for a specific interview type
    """
    try:
        query = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_type == interview_type
        )
        
        if difficulty:
            query = query.filter(InterviewQuestion.difficulty_level == difficulty)
        
        questions = query.all()
        
        return {
            "count": len(questions),
            "questions": [
                {
                    "question_id": q.question_id,
                    "question_text": q.question_text,
                    "difficulty": q.difficulty_level,
                    "category": q.category
                }
                for q in questions
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/session/{session_id}")
async def get_session_details(session_id: str, db: SessionLocal = Depends(get_db)):
    """
    Get details of a specific interview session
    """
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        responses = db.query(SessionResponse).filter(
            SessionResponse.session_id == session_id
        ).all()
        
        return {
            "session_id": session.session_id,
            "interview_type": session.interview_type,
            "difficulty": session.difficulty_level,
            "status": session.status,
            "started_at": session.started_at,
            "completed_at": session.completed_at,
            "overall_score": session.overall_score,
            "overall_rating": session.overall_rating,
            "responses_count": len(responses)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Helper functions

def get_questions_for_interview(interview_type: str, difficulty: str, company: Optional[str], duration: int, db: SessionLocal):
    """
    Retrieve appropriate questions based on interview parameters
    """
    # Calculate number of questions based on duration
    questions_per_10min = 5
    num_questions = (duration // 10) * questions_per_10min
    
    # Query questions
    query = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_type == interview_type,
        InterviewQuestion.difficulty_level == difficulty
    )
    
    if company:
        query = query.filter(InterviewQuestion.company == company)
    
    questions = query.limit(num_questions).all()
    
    return [
        {
            "question_id": q.question_id,
            "question_text": q.question_text,
            "category": q.category,
            "expected_keywords": q.expected_keywords
        }
        for q in questions
    ]

def generate_response_feedback(analysis: Dict[str, Any]) -> List[tuple]:
    """
    Generate specific feedback items based on analysis
    """
    feedback_items = []
    features = analysis['features']
    scores = analysis['scores']
    
    # Filler words feedback
    if features['filler_word_count'] > 5:
        feedback_items.append((
            f"Try to reduce filler words (found {features['filler_word_count']}). Practice pausing instead of using 'um', 'like', or 'you know'.",
            "improvement"
        ))
    elif features['filler_word_count'] <= 2:
        feedback_items.append((
            "Excellent control of filler words! Your speech is clear and professional.",
            "strength"
        ))
    
    # Response length feedback
    if features['word_count'] < 30:
        feedback_items.append((
            "Your answer was quite brief. Try to provide more detailed explanations with examples.",
            "improvement"
        ))
    elif features['word_count'] > 200:
        feedback_items.append((
            "Very detailed response! Make sure to stay focused on the key points.",
            "strength"
        ))
    
    # Technical terminology feedback
    if features['technical_term_count'] == 0 and 'technical' in analysis.get('interview_type', ''):
        feedback_items.append((
            "Include more technical terminology relevant to the question.",
            "improvement"
        ))
    elif features['technical_term_count'] >= 3:
        feedback_items.append((
            "Great use of relevant technical terminology!",
            "strength"
        ))
    
    # Structure feedback
    if features.get('has_structure', False):
        feedback_items.append((
            "Well-structured response with clear beginning, middle, and end.",
            "strength"
        ))
    else:
        feedback_items.append((
            "Try to structure your answer: provide context, explain the concept, and give examples.",
            "improvement"
        ))
    
    # Examples feedback
    if features.get('has_examples', False):
        feedback_items.append((
            "Excellent use of examples to illustrate your points!",
            "strength"
        ))
    else:
        feedback_items.append((
            "Consider adding specific examples to make your answer more concrete.",
            "suggestion"
        ))
    
    # Confidence feedback
    if features.get('confidence_score', 0) < 0:
        feedback_items.append((
            "Use more confident language. Replace 'maybe' and 'I think' with 'I recommend' or 'The best approach is'.",
            "improvement"
        ))
    elif features.get('confidence_score', 0) > 2:
        feedback_items.append((
            "Confident and assertive delivery!",
            "strength"
        ))
    
    return feedback_items

def calculate_overall_feedback(responses: List[SessionResponse], db: SessionLocal) -> Dict[str, Any]:
    """
    Calculate comprehensive feedback across all responses
    """
    if not responses:
        return {
            "overall_score": 0.0,
            "overall_rating": "incomplete",
            "strengths": [],
            "improvements": [],
            "detailed_metrics": {}
        }
    
    # Calculate averages
    avg_content = sum(r.content_quality_score for r in responses) / len(responses)
    avg_communication = sum(r.communication_score for r in responses) / len(responses)
    avg_confidence = sum(r.confidence_score for r in responses) / len(responses)
    avg_technical = sum(r.technical_accuracy_score for r in responses) / len(responses)
    
    overall_score = (avg_content + avg_communication + avg_confidence + avg_technical) / 4
    
    # Determine overall rating
    if overall_score >= 8.5:
        overall_rating = "excellent"
    elif overall_score >= 7.0:
        overall_rating = "good"
    elif overall_score >= 5.0:
        overall_rating = "average"
    else:
        overall_rating = "needs_improvement"
    
    # Aggregate metrics
    total_words = sum(r.word_count for r in responses)
    total_filler_words = sum(r.filler_word_count for r in responses)
    total_tech_terms = sum(r.technical_term_count for r in responses)
    avg_word_length = sum(r.average_word_length for r in responses) / len(responses)
    
    # Identify strengths and improvements
    strengths = []
    improvements = []
    
    if avg_communication >= 8.0:
        strengths.append("Excellent communication skills with clear articulation")
    if avg_technical >= 8.0:
        strengths.append("Strong technical knowledge and accurate explanations")
    if avg_confidence >= 8.0:
        strengths.append("Confident and assertive delivery throughout")
    if total_filler_words / len(responses) <= 2:
        strengths.append("Professional speech with minimal filler words")
    
    if avg_communication < 6.0:
        improvements.append("Work on clarity and structure of responses")
    if avg_technical < 6.0:
        improvements.append("Deepen technical knowledge in key areas")
    if avg_confidence < 6.0:
        improvements.append("Practice to build confidence in your delivery")
    if total_filler_words / len(responses) > 5:
        improvements.append("Reduce filler words through practice and pausing")
    
    detailed_metrics = {
        "average_scores": {
            "content_quality": round(avg_content, 2),
            "communication": round(avg_communication, 2),
            "confidence": round(avg_confidence, 2),
            "technical_accuracy": round(avg_technical, 2)
        },
        "aggregated_stats": {
            "total_words": total_words,
            "avg_words_per_response": round(total_words / len(responses), 2),
            "total_filler_words": total_filler_words,
            "filler_word_rate": round((total_filler_words / total_words) * 100, 2),
            "technical_terms_used": total_tech_terms,
            "avg_word_length": round(avg_word_length, 2)
        },
        "performance_trend": analyze_performance_trend(responses)
    }
    
    return {
        "overall_score": round(overall_score, 2),
        "overall_rating": overall_rating,
        "strengths": strengths,
        "improvements": improvements,
        "detailed_metrics": detailed_metrics
    }

def analyze_performance_trend(responses: List[SessionResponse]) -> Dict[str, Any]:
    """
    Analyze if performance improved/declined throughout interview
    """
    if len(responses) < 3:
        return {"trend": "insufficient_data"}
    
    first_third_avg = sum(r.overall_response_score for r in responses[:len(responses)//3]) / (len(responses)//3)
    last_third_avg = sum(r.overall_response_score for r in responses[-len(responses)//3:]) / (len(responses)//3)
    
    difference = last_third_avg - first_third_avg
    
    if difference > 1.0:
        trend = "improving"
        message = "Great job! Your performance improved as the interview progressed."
    elif difference < -1.0:
        trend = "declining"
        message = "Consider practicing stamina - performance declined toward the end."
    else:
        trend = "consistent"
        message = "Consistent performance throughout the interview."
    
    return {
        "trend": trend,
        "message": message,
        "first_third_score": round(first_third_avg, 2),
        "last_third_score": round(last_third_avg, 2),
        "improvement": round(difference, 2)
    }

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## ML Service Module

```python
# ml_service.py

import joblib
import numpy as np
from typing import Dict, Any
from feature_extraction import ResponseFeatureExtractor

class InterviewAnalyzer:
    """
    Service class for analyzing interview responses using trained ML model
    """
    
    def __init__(self, model_path='models/interview_classifier.pkl'):
        """
        Load trained ML model and dependencies
        """
        try:
            model_data = joblib.load(model_path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_names = model_data['feature_names']
            self.feature_extractor = model_data.get('feature_extractor', ResponseFeatureExtractor())
            print(f"ML Model loaded successfully from {model_path}")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Initializing with default feature extractor")
            self.model = None
            self.scaler = None
            self.feature_names = None
            self.feature_extractor = ResponseFeatureExtractor()
    
    def analyze_response(self, response_text: str, question_text: str = '', interview_type: str = 'technical_software') -> Dict[str, Any]:
        """
        Comprehensive analysis of a single interview response
        """
        # Extract features
        features = self.feature_extractor.extract_all_features(
            response_text, question_text, interview_type
        )
        
        # Get ML prediction if model is loaded
        if self.model and self.scaler:
            ml_prediction = self._get_ml_prediction(features)
        else:
            ml_prediction = self._get_rule_based_prediction(features)
        
        # Calculate individual scores
        scores = self._calculate_component_scores(features, response_text, interview_type)
        
        # Calculate overall score
        overall_score = (
            scores['content_quality'] * 0.35 +
            scores['communication'] * 0.25 +
            scores['confidence'] * 0.20 +
            scores['technical_accuracy'] * 0.20
        )
        
        # Determine rating
        rating = self._score_to_rating(overall_score)
        
        return {
            'overall_score': round(overall_score, 2),
            'rating': rating,
            'scores': scores,
            'features': features,
            'ml_prediction': ml_prediction,
            'interview_type': interview_type
        }
    
    def _get_ml_prediction(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get prediction from trained ML model
        """
        try:
            import pandas as pd
            
            # Convert features to DataFrame
            X = pd.DataFrame([features])[self.feature_names]
            
            # Scale features
            X_scaled = self.scaler.transform(X)
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            probabilities = self.model.predict_proba(X_scaled)[0]
            confidence = max(probabilities)
            
            return {
                'prediction': prediction,
                'confidence': round(confidence, 3),
                'probabilities': {
                    class_label: round(prob, 3)
                    for class_label, prob in zip(self.model.classes_, probabilities)
                }
            }
        except Exception as e:
            print(f"ML prediction error: {e}")
            return {'prediction': 'unknown', 'confidence': 0.0}
    
    def _get_rule_based_prediction(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback rule-based prediction if ML model not available
        """
        score = 0
        
        # Word count scoring
        if features['word_count'] >= 50:
            score += 2.5
        elif features['word_count'] >= 30:
            score += 1.5
        
        # Filler words penalty
        if features['filler_word_count'] <= 2:
            score += 2.0
        elif features['filler_word_count'] <= 5:
            score += 1.0
        else:
            score -= 1.0
        
        # Technical terms
        if features['technical_term_count'] >= 3:
            score += 2.0
        elif features['technical_term_count'] >= 1:
            score += 1.0
        
        # Structure bonus
        if features.get('has_structure', False):
            score += 1.5
        
        # Examples bonus
        if features.get('has_examples', False):
            score += 1.0
        
        # Confidence
        if features.get('confidence_score', 0) > 0:
            score += 1.0
        elif features.get('confidence_score', 0) < 0:
            score -= 0.5
        
        # Normalize to 0-10 scale
        normalized_score = min(max(score, 0), 10)
        rating = self._score_to_rating(normalized_score)
        
        return {
            'prediction': rating,
            'confidence': 0.7,
            'method': 'rule_based'
        }
    
    def _calculate_component_scores(self, features: Dict[str, Any], response_text: str, interview_type: str) -> Dict[str, float]:
        """
        Calculate individual component scores
        """
        # Content Quality Score (0-10)
        content_score = 5.0  # Base score
        
        if features['word_count'] >= 50:
            content_score += 2.0
        elif features['word_count'] >= 30:
            content_score += 1.0
        elif features['word_count'] < 20:
            content_score -= 2.0
        
        if features.get('has_structure', False):
            content_score += 1.5
        
        if features.get('has_examples', False):
            content_score += 1.5
        
        if features.get('relevance_score', 0) > 0.5:
            content_score += 1.0
        
        # Communication Score (0-10)
        communication_score = 5.0
        
        if features['filler_word_ratio'] <= 0.02:
            communication_score += 3.0
        elif features['filler_word_ratio'] <= 0.05:
            communication_score += 1.5
        else:
            communication_score -= 2.0
        
        if features['avg_sentence_length'] >= 10 and features['avg_sentence_length'] <= 20:
            communication_score += 1.5
        
        if features['unique_word_ratio'] > 0.7:
            communication_score += 0.5
        
        # Confidence Score (0-10)
        confidence_score = 5.0
        
        if features.get('confidence_score', 0) > 2:
            confidence_score += 3.0
        elif features.get('confidence_score', 0) > 0:
            confidence_score += 1.5
        elif features.get('confidence_score', 0) < -2:
            confidence_score -= 2.0
        
        if features.get('starts_with_context', False):
            confidence_score += 1.0
        
        if features['word_count'] >= 40:
            confidence_score += 1.0
        
        # Technical Accuracy Score (0-10)
        technical_score = 5.0
        
        if 'technical' in interview_type:
            if features['technical_term_count'] >= 5:
                technical_score += 3.0
            elif features['technical_term_count'] >= 3:
                technical_score += 2.0
            elif features['technical_term_count'] >= 1:
                technical_score += 1.0
            else:
                technical_score -= 2.0
        
        if features.get('relevance_score', 0) > 0.6:
            technical_score += 2.0
        elif features.get('relevance_score', 0) > 0.4:
            technical_score += 1.0
        
        # Normalize all scores to 0-10 range
        return {
            'content_quality': min(max(content_score, 0), 10),
            'communication': min(max(communication_score, 0), 10),
            'confidence': min(max(confidence_score, 0), 10),
            'technical_accuracy': min(max(technical_score, 0), 10)
        }
    
    def _score_to_rating(self, score: float) -> str:
        """
        Convert numerical score to rating category
        """
        if score >= 8.5:
            return 'excellent'
        elif score >= 7.0:
            return 'good'
        elif score >= 5.0:
            return 'average'
        else:
            return 'poor'
    
    def batch_analyze(self, responses: list) -> list:
        """
        Analyze multiple responses in batch
        """
        results = []
        for response_data in responses:
            analysis = self.analyze_response(
                response_text=response_data['response_text'],
                question_text=response_data.get('question_text', ''),
                interview_type=response_data.get('interview_type', 'technical_software')
            )
            results.append(analysis)
        return results
```

---

## VAPI Integration Module

```python
# vapi_service.py

import os
from typing import Dict, List, Any
import requests
from dotenv import load_dotenv

load_dotenv()

class VAPIManager:
    """
    Manager class for VAPI voice assistant integration
    """
    
    def __init__(self):
        self.api_key = os.getenv('VAPI_API_KEY')
        self.base_url = 'https://api.vapi.ai'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_assistant_config(self, session_id: str, interview_type: str, questions: List[str]) -> Dict[str, Any]:
        """
        Create VAPI assistant configuration for interview session
        """
        # Create system prompt based on interview type
        system_prompt = self._generate_system_prompt(interview_type, questions)
        
        config = {
            'model': {
                'provider': 'openai',
                'model': 'gpt-4',
                'messages': [
                    {
                        'role': 'system',
                        'content': system_prompt
                    }
                ],
                'temperature': 0.7
            },
            'voice': {
                'provider': 'elevenlabs',  # or '11labs', 'playht'
                'voiceId': 'professional_interviewer_voice_id'
            },
            'firstMessage': self._get_first_message(interview_type),
            'endCallFunctionEnabled': True,
            'recordingEnabled': True,
            'serverUrl': f'{os.getenv("BACKEND_URL")}/api/vapi/webhook',
            'serverUrlSecret': os.getenv('VAPI_WEBHOOK_SECRET'),
            'metadata': {
                'session_id': session_id,
                'interview_type': interview_type
            }
        }
        
        return config
    
    def _generate_system_prompt(self, interview_type: str, questions: List[str]) -> str:
        """
        Generate appropriate system prompt for the AI interviewer
        """
        base_prompt = f"""You are a professional interviewer conducting a {interview_type} interview. 

Your role:
1. Ask questions one at a time from the provided list
2. Listen carefully to complete answers
3. Provide brief acknowledgments between questions
4. Maintain a professional, encouraging tone
5. If an answer is unclear, ask one follow-up question for clarification
6. Do not provide the correct answer or extensive feedback during the interview
7. Keep the conversation flowing naturally

Questions to ask in order:
{chr(10).join(f"{i+1}. {q}" for i, q in enumerate(questions))}

Instructions:
- Start with a warm greeting and explain that this is a mock interview
- Ask questions sequentially
- After each answer, give brief positive acknowledgment ("Thank you", "I see", "Interesting")
- Move to the next question smoothly
- After all questions, thank the candidate and end the interview
- Keep your responses concise and professional"""

        if 'technical' in interview_type:
            base_prompt += "\n\nFor technical questions, listen for key concepts, algorithms, and technical terminology."
        elif 'behavioral' in interview_type:
            base_prompt += "\n\nFor behavioral questions, listen for specific examples using the STAR method (Situation, Task, Action, Result)."
        
        return base_prompt
    
    def _get_first_message(self, interview_type: str) -> str:
        """
        Generate appropriate first message from AI interviewer
        """
        messages = {
            'technical_software': "Hello! I'm your AI interviewer today. We'll be conducting a technical software engineering interview. I'll ask you several questions, and please take your time to think through your answers. Are you ready to begin?",
            'technical_data': "Hello! Welcome to your data science technical interview. I'll be asking you questions about data analysis, machine learning, and related topics. Feel free to explain your thought process as you answer. Ready to start?",
            'behavioral': "Hi there! I'll be conducting your behavioral interview today. I'll ask about your past experiences and how you've handled various situations. Please provide specific examples when answering. Shall we begin?",
            'system_design': "Hello! Today we'll focus on system design. I'll present scenarios where you'll need to design scalable systems. Think aloud as you work through the problems. Ready when you are!"
        }
        
        return messages.get(interview_type, "Hello! Welcome to your mock interview. Let's begin!")
    
    def create_assistant(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new VAPI assistant
        """
        try:
            response = requests.post(
                f'{self.base_url}/assistant',
                headers=self.headers,
                json=config
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error creating VAPI assistant: {e}")
            return {}
    
    def handle_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle webhook callbacks from VAPI
        """
        event_type = webhook_data.get('type')
        
        if event_type == 'transcript':
            return self._handle_transcript(webhook_data)
        elif event_type == 'call-end':
            return self._handle_call_end(webhook_data)
        elif event_type == 'function-call':
            return self._handle_function_call(webhook_data)
        
        return {'status': 'received'}
    
    def _handle_transcript(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process transcript from VAPI
        """
        transcript_text = data.get('transcript', {}).get('text', '')
        role = data.get('transcript', {}).get('role', '')        pip install pytest pytest-asyncio
        cd ai-mock-interview-backend
        python -m pytest tests/test_ml_service.py -v
        session_id = data.get('metadata', {}).get('session_id')
        
        return {
            'status': 'processed',
            'session_id': session_id,
            'transcript': transcript_text,
            'role': role
        }
    
    def _handle_call_end(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle call end event
        """
        session_id = data.get('metadata', {}).get('session_id')
        duration = data.get('call', {}).get('duration')
        
        return {
            'status': 'call_ended',
            'session_id': session_id,
            'duration': duration
        }
    
    def _handle_function_call(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle custom function calls from VAPI
        """
        function_name = data.get('functionCall', {}).get('name')
        parameters = data.get('functionCall', {}).get('parameters', {})
        
        # Implement custom function logic here
        return {
            'result': f"Function {function_name} executed"
        }
```

---

## Database Models

```python
# models.py

from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, Boolean, ARRAY, JSON