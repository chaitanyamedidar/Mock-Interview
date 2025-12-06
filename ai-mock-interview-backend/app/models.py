from sqlalchemy import Column, Integer, String, Text, DECIMAL, TIMESTAMP, Boolean, JSON
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
    expected_keywords = Column(JSON, nullable=True)  # Store as JSON for SQLite compatibility
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