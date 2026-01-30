import pytest
import json
from datetime import datetime
from app.vapi_interview_service import VAPIInterviewAnalyzer

@pytest.fixture
def analyzer():
    """Create VAPIInterviewAnalyzer instance."""
    return VAPIInterviewAnalyzer()

@pytest.fixture
def sample_messages():
    """Sample VAPI transcript messages."""
    return [
        {
            "role": "assistant",
            "message": "Tell me about yourself.",
            "timestamp": "2026-01-29T10:00:00Z"
        },
        {
            "role": "user",
            "message": "I am a software engineer with 5 years of experience in Python and JavaScript.",
            "timestamp": "2026-01-29T10:00:30Z"
        },
        {
            "role": "assistant",
            "message": "What is your experience with databases?",
            "timestamp": "2026-01-29T10:00:45Z"
        },
        {
            "role": "user",
            "message": "I have worked extensively with PostgreSQL, MongoDB, and Redis. I understand database design, indexing, and query optimization.",
            "timestamp": "2026-01-29T10:01:20Z"
        }
    ]

def test_extract_qa_pairs(analyzer, sample_messages):
    """Test extraction of Q&A pairs from transcript."""
    qa_pairs = analyzer.extract_qa_pairs(sample_messages)
    
    assert len(qa_pairs) == 2
    assert qa_pairs[0]['question'] == "Tell me about yourself."
    assert "software engineer" in qa_pairs[0]['answer']
    assert qa_pairs[1]['question'] == "What is your experience with databases?"
    assert "PostgreSQL" in qa_pairs[1]['answer']

def test_calculate_communication_score(analyzer):
    """Test communication score calculation."""
    qa_pairs = [
        {
            "question": "Test question?",
            "answer": "This is a clear answer without filler words. I explain concepts well."
        },
        {
            "question": "Another question?",
            "answer": "Um, well, like, you know, I think this is, uh, basically the answer."
        }
    ]
    
    # First set should score higher (no filler words)
    score1 = analyzer.calculate_communication_score([qa_pairs[0]], 60)
    score2 = analyzer.calculate_communication_score([qa_pairs[1]], 60)
    
    assert score1 > score2
    assert 0 <= score1 <= 100
    assert 0 <= score2 <= 100

def test_calculate_time_management_score(analyzer):
    """Test time management score calculation."""
    # Good scenario: all questions answered, reasonable lengths
    qa_pairs = [
        {"question": "Q1", "answer": "A " * 50},  # ~50 words
        {"question": "Q2", "answer": "A " * 50},
        {"question": "Q3", "answer": "A " * 50}
    ]
    
    score = analyzer.calculate_time_management_score(qa_pairs, 900, 3)  # 15 minutes
    
    assert 0 <= score <= 100
    assert score >= 75  # Should be good score for completing all questions

def test_detect_technical_keywords(analyzer):
    """Test technical keyword detection."""
    qa_pairs = [
        {
            "question": "Explain your approach",
            "answer": "I used an algorithm with optimal time complexity. The data structure was a hash table for O(1) lookups."
        }
    ]
    
    keywords = analyzer.detect_technical_keywords(qa_pairs, 'technical_software')
    
    assert 'algorithm' in keywords
    assert 'complexity' in keywords
    assert 'data structure' in keywords

def test_get_performance_label(analyzer):
    """Test performance label generation."""
    assert analyzer.get_performance_label(95) == "Excellent"
    assert analyzer.get_performance_label(85) == "Strong Performance"
    assert analyzer.get_performance_label(75) == "Good"
    assert analyzer.get_performance_label(65) == "Average"
    assert analyzer.get_performance_label(55) == "Needs Improvement"

def test_generate_recommendations(analyzer):
    """Test recommendation generation."""
    llm_analysis = {
        'specific_improvements': [
            'Practice explaining technical concepts more clearly',
            'Provide more specific examples from your experience'
        ]
    }
    
    recommendations = analyzer.generate_recommendations(
        llm_analysis,
        communication_score=65,  # Low score should trigger generic recommendation
        technical_skills_score=80,
        problem_solving_score=75,
        time_management_score=70
    )
    
    assert len(recommendations) <= 5
    assert any('Filler Words' in rec['title'] for rec in recommendations)
    assert all('title' in rec and 'description' in rec for rec in recommendations)

def test_calculate_answer_durations(analyzer, sample_messages):
    """Test answer duration calculation."""
    durations = analyzer.calculate_answer_durations(sample_messages)
    
    # Should have durations for user messages
    assert len(durations) >= 1
    assert all(d >= 0 for d in durations)
