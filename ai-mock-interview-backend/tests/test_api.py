import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from main import app
from database import get_db, Base
from models import InterviewSession, InterviewQuestion, SessionResponse

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_interview.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_client():
    """Create test client and database"""
    Base.metadata.create_all(bind=engine)
    
    # Seed test data
    db = TestingSessionLocal()
    
    # Add test questions
    test_questions = [
        InterviewQuestion(
            question_text="What is REST API?",
            interview_type="technical_software",
            difficulty_level="intermediate",
            category="web_development",
            expected_keywords=["REST", "API", "HTTP"]
        ),
        InterviewQuestion(
            question_text="Tell me about a challenging project",
            interview_type="behavioral", 
            difficulty_level="intermediate",
            category="problem_solving",
            expected_keywords=["challenge", "project", "solution"]
        )
    ]
    
    for question in test_questions:
        db.add(question)
    db.commit()
    db.close()
    
    client = TestClient(app)
    yield client
    
    # Cleanup
    Base.metadata.drop_all(bind=engine)

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_root_endpoint(self, test_client):
        """Test root health check"""
        response = test_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "online"
        assert "version" in data
    
    def test_health_endpoint(self, test_client):
        """Test detailed health check"""
        response = test_client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

class TestInterviewAPI:
    """Test interview management endpoints"""
    
    def test_start_interview_success(self, test_client):
        """Test starting a new interview"""
        request_data = {
            "interview_type": "technical_software",
            "difficulty": "intermediate",
            "duration": 30
        }
        
        response = test_client.post("/api/interview/start", json=request_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "session_id" in data
        assert "questions" in data
        assert "vapi_config" in data
        assert len(data["questions"]) > 0
    
    def test_start_interview_invalid_data(self, test_client):
        """Test starting interview with invalid data"""
        request_data = {
            "interview_type": "invalid_type",
            "difficulty": "intermediate",
            "duration": 5  # Too short
        }
        
        response = test_client.post("/api/interview/start", json=request_data)
        assert response.status_code == 422  # Validation error
    
    def test_analyze_response_success(self, test_client):
        """Test analyzing a response"""
        # First start an interview
        start_response = test_client.post("/api/interview/start", json={
            "interview_type": "technical_software",
            "difficulty": "intermediate", 
            "duration": 20
        })
        
        session_data = start_response.json()
        session_id = session_data["session_id"]
        question_id = session_data["questions"][0]["question_id"]
        
        # Analyze a response
        analysis_request = {
            "session_id": session_id,
            "response_text": "REST API is an architectural style that uses HTTP methods like GET, POST, PUT, and DELETE to interact with resources. It's stateless and follows client-server architecture.",
            "question_id": question_id,
            "question_number": 1
        }
        
        response = test_client.post("/api/interview/analyze-response", json=analysis_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "response_id" in data
        assert "quality_score" in data
        assert "rating" in data
        assert "feedback" in data
        assert data["quality_score"] >= 0
        assert data["quality_score"] <= 10
    
    def test_analyze_response_invalid_session(self, test_client):
        """Test analyzing response with invalid session"""
        analysis_request = {
            "session_id": "invalid-session-id",
            "response_text": "Some response text",
            "question_id": 999,
            "question_number": 1
        }
        
        response = test_client.post("/api/interview/analyze-response", json=analysis_request)
        assert response.status_code == 404
    
    def test_end_interview_success(self, test_client):
        """Test ending an interview"""
        # Start interview and add responses
        start_response = test_client.post("/api/interview/start", json={
            "interview_type": "behavioral",
            "difficulty": "intermediate",
            "duration": 20
        })
        
        session_data = start_response.json()
        session_id = session_data["session_id"]
        question_id = session_data["questions"][0]["question_id"]
        
        # Add a response
        test_client.post("/api/interview/analyze-response", json={
            "session_id": session_id,
            "response_text": "I faced a challenging project when I had to redesign our entire user authentication system. The situation was that we were experiencing security vulnerabilities. My task was to implement a more secure system without disrupting existing users. I researched best practices, implemented OAuth 2.0, and conducted thorough testing. The result was a 50% reduction in security issues and improved user experience.",
            "question_id": question_id,
            "question_number": 1
        })
        
        # End interview
        end_response = test_client.post("/api/interview/end", json={
            "session_id": session_id
        })
        
        assert end_response.status_code == 200
        
        data = end_response.json()
        assert data["session_id"] == session_id
        assert "overall_score" in data
        assert "overall_rating" in data
        assert "strengths" in data
        assert "improvements" in data
        assert "question_breakdown" in data
    
    def test_end_interview_no_responses(self, test_client):
        """Test ending interview with no responses"""
        # Start interview but don't add responses
        start_response = test_client.post("/api/interview/start", json={
            "interview_type": "technical_software",
            "difficulty": "intermediate",
            "duration": 15
        })
        
        session_id = start_response.json()["session_id"]
        
        # Try to end interview
        end_response = test_client.post("/api/interview/end", json={
            "session_id": session_id
        })
        
        assert end_response.status_code == 400  # No responses found

class TestQuestionAPI:
    """Test question management endpoints"""
    
    def test_get_questions_by_type(self, test_client):
        """Test getting questions by type"""
        response = test_client.get("/api/questions/technical_software")
        assert response.status_code == 200
        
        data = response.json()
        assert "questions" in data
        assert "count" in data
        assert data["count"] >= 0
    
    def test_get_questions_with_filters(self, test_client):
        """Test getting questions with difficulty filter"""
        response = test_client.get("/api/questions/technical_software?difficulty=intermediate")
        assert response.status_code == 200
        
        data = response.json()
        assert "questions" in data
        
        # Check that all returned questions have intermediate difficulty
        for question in data["questions"]:
            assert question["difficulty"] == "intermediate"
    
    def test_get_questions_invalid_type(self, test_client):
        """Test getting questions with invalid type"""
        response = test_client.get("/api/questions/invalid_type")
        assert response.status_code == 200
        
        data = response.json()
        assert data["count"] == 0

class TestSessionAPI:
    """Test session management endpoints"""
    
    def test_get_session_details(self, test_client):
        """Test getting session details"""
        # Create a session first
        start_response = test_client.post("/api/interview/start", json={
            "interview_type": "technical_software",
            "difficulty": "intermediate",
            "duration": 25
        })
        
        session_id = start_response.json()["session_id"]
        
        # Get session details
        response = test_client.get(f"/api/session/{session_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["session_id"] == session_id
        assert "interview_type" in data
        assert "difficulty_level" in data
        assert "status" in data
        assert "started_at" in data
    
    def test_get_session_details_invalid_id(self, test_client):
        """Test getting details for invalid session"""
        response = test_client.get("/api/session/invalid-session-id")
        assert response.status_code == 404

class TestVAPIWebhook:
    """Test VAPI webhook handling"""
    
    def test_webhook_transcript(self, test_client):
        """Test handling transcript webhook"""
        webhook_data = {
            "type": "transcript",
            "transcript": {
                "text": "This is a test transcript",
                "isFinal": True
            }
        }
        
        response = test_client.post("/api/vapi/webhook", json=webhook_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
    
    def test_webhook_function_call(self, test_client):
        """Test handling function call webhook"""
        webhook_data = {
            "type": "function-call",
            "functionCall": {
                "name": "analyze_response",
                "parameters": {
                    "session_id": "test-session",
                    "question_number": 1,
                    "response_text": "Test response"
                }
            }
        }
        
        response = test_client.post("/api/vapi/webhook", json=webhook_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "result" in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])