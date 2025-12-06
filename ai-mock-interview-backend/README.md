# AI Mock Interview Backend

A comprehensive FastAPI backend for an AI-powered mock interview platform with VAPI voice integration and machine learning-based response analysis.

## 🚀 Features

- **Voice Interview Integration** with VAPI
- **ML-powered Response Analysis** using scikit-learn
- **Real-time Feedback Generation**
- **Comprehensive Question Database** (50+ questions)
- **Multiple Interview Types** (Technical, Behavioral, Company-specific)
- **RESTful API** with automatic documentation
- **Database Support** (PostgreSQL/SQLite)
- **Webhook Integration** for real-time processing

## 📋 Prerequisites

- Python 3.9+
- PostgreSQL (optional, SQLite for development)
- VAPI Account and API Key

## 🛠️ Installation

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-mock-interview-backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configurations
```

Required environment variables:
```env
DATABASE_URL=sqlite:///./interview_platform.db
VAPI_API_KEY=your_vapi_api_key_here
VAPI_WEBHOOK_SECRET=your_webhook_secret_here
BACKEND_URL=http://localhost:8000
```

### 3. Database Setup

```bash
# Initialize database and seed questions
python backend/database.py
```

### 4. Train ML Model (Optional)

```bash
# Train the ML model for response analysis
python backend/model_training.py
```

### 5. Run the Application

```bash
# Development server
uvicorn backend.main:app --reload --port 8000

# Production server
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Base**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📚 API Endpoints

### Interview Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/interview/start` | Start new interview session |
| POST | `/api/interview/analyze-response` | Analyze individual response |
| POST | `/api/interview/end` | End interview and get feedback |
| GET | `/api/session/{session_id}` | Get session details |

### Question Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/questions/{interview_type}` | Get questions by type |
| GET | `/api/questions/{interview_type}?difficulty=intermediate` | Filter by difficulty |

### VAPI Integration

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/vapi/webhook` | Handle VAPI webhooks |

### Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Basic health check |
| GET | `/health` | Detailed health status |

## 🔧 Usage Examples

### Start Interview Session

```python
import requests

response = requests.post("http://localhost:8000/api/interview/start", json={
    "interview_type": "technical_software",
    "difficulty": "intermediate", 
    "duration": 30,
    "company": "google"  # optional
})

session_data = response.json()
print(f"Session ID: {session_data['session_id']}")
```

### Analyze Response

```python
response = requests.post("http://localhost:8000/api/interview/analyze-response", json={
    "session_id": "your-session-id",
    "response_text": "REST API is an architectural style...",
    "question_id": 1,
    "question_number": 1
})

analysis = response.json()
print(f"Quality Score: {analysis['quality_score']}")
print(f"Rating: {analysis['rating']}")
```

## 🤖 Machine Learning Features

### Response Analysis Metrics

- **Content Quality**: Depth, structure, examples
- **Communication**: Clarity, filler words, flow
- **Confidence**: Assertiveness, certainty indicators
- **Technical Accuracy**: Domain knowledge, terminology

### Feature Extraction

- Text statistics (word count, sentence structure)
- Filler word detection and counting
- Technical terminology analysis
- Confidence indicators
- Response structure analysis
- Language complexity metrics

### Model Training

The system uses a Random Forest classifier trained on:
- 200+ synthetic training samples
- Feature engineering from text analysis
- Multi-class classification (excellent, good, average, poor)

## 🗃️ Database Schema

### Core Tables

- **interview_sessions**: Session metadata and results
- **interview_questions**: Question database with categorization
- **session_responses**: Individual response records
- **feedback_details**: Detailed feedback items
- **ml_training_data**: Continuous learning data

## 🔌 VAPI Integration

### Features

- **Automated Interview Conductor**: AI assistant asks questions
- **Real-time Transcription**: Speech-to-text processing
- **Function Calling**: Trigger analysis during conversation
- **Webhook Processing**: Handle real-time events

### Configuration

```python
vapi_config = {
    "model": "gpt-3.5-turbo",
    "voice": "professional_female",
    "transcriber": "deepgram",
    "functions": ["analyze_response", "end_interview"]
}
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=backend tests/

# Test specific endpoint
pytest tests/test_interview_api.py::test_start_interview
```

## 📦 Deployment

### Docker Deployment

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend/
COPY models/ ./models/

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

```env
DATABASE_URL=postgresql://user:password@db:5432/interview_db
VAPI_API_KEY=prod_vapi_key
BACKEND_URL=https://your-api-domain.com
DEBUG=False
```

## 🔧 Configuration

### Interview Types Supported

- `technical_software`: Software engineering questions
- `behavioral`: Behavioral and situational questions
- `system_design`: Architecture and design questions

### Difficulty Levels

- `entry`: Junior level questions
- `intermediate`: Mid-level questions
- `advanced`: Senior level questions

### Companies Supported

- `google`: Google-specific questions
- `amazon`: Amazon-specific questions
- `microsoft`: Microsoft-specific questions
- Generic questions (no company specified)

## 📊 Monitoring and Logging

### Logging Configuration

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/application.log'),
        logging.StreamHandler()
    ]
)
```

### Health Monitoring

```bash
# Check API health
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "ml_model": "loaded",
    "vapi": "configured"
  }
}
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-feature`
3. **Make changes and test**: `pytest tests/`
4. **Commit changes**: `git commit -am 'Add new feature'`
5. **Push to branch**: `git push origin feature/new-feature`
6. **Create Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write tests for new features
- Update documentation
- Use meaningful commit messages

## 🔒 Security

### Best Practices Implemented

- **Environment Variables**: Sensitive data in .env
- **Webhook Signature Validation**: VAPI webhook security
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Prevention**: SQLAlchemy ORM
- **CORS Configuration**: Controlled cross-origin access

## 📈 Performance

### Optimization Features

- **Connection Pooling**: Database connection management
- **Async Processing**: FastAPI async endpoints
- **Model Caching**: ML model loaded once at startup
- **Batch Processing**: Multiple response analysis

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check DATABASE_URL in .env
# Ensure PostgreSQL is running
# For SQLite, check file permissions
```

**ML Model Not Loading**
```bash
# Train the model first
python backend/model_training.py

# Check model file exists
ls models/interview_classifier.pkl
```

**VAPI Webhook Issues**
```bash
# Verify webhook URL is publicly accessible
# Check VAPI_WEBHOOK_SECRET in .env
# Ensure proper SSL certificate for HTTPS
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **FastAPI** for the excellent web framework
- **VAPI** for voice AI integration
- **scikit-learn** for machine learning capabilities
- **SQLAlchemy** for database ORM

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation at `/docs`
- Review the troubleshooting section

---

**Version**: 1.0.0  
**Last Updated**: October 2025