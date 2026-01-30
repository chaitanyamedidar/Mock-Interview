import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from app.gcp_gemini_service import GCPGeminiService

@pytest.fixture
def mock_genai():
    """Mock google.generativeai module."""
    with patch('app.gcp_gemini_service.genai') as mock:
        yield mock

@pytest.fixture
def gemini_service(mock_genai):
    """Create GCPGeminiService instance with mocked API."""
    with patch.dict('os.environ', {'GOOGLE_AI_API_KEY': 'test_key'}):
        return GCPGeminiService()

@pytest.mark.asyncio
async def test_analyze_resume_valid_input(gemini_service):
    """Test resume analysis with valid input."""
    mock_response = Mock()
    mock_response.text = '''{
        "ats_score": 85,
        "scores": {
            "keyword_match": 80,
            "format_quality": 90,
            "experience_relevance": 85,
            "skills_match": 88,
            "achievements_quantified": 75,
            "overall_presentation": 90
        },
        "strengths": ["Strong technical skills", "Clear formatting", "Quantified achievements"],
        "improvements": ["Add more keywords", "Expand summary"],
        "missing_keywords": ["Python", "AWS"],
        "summary": "Well-structured resume with strong technical background."
    }'''
    
    with patch.object(gemini_service.model, 'generate_content', return_value=mock_response):
        result = await gemini_service.analyze_resume(
            "Software Engineer with 5 years experience",
            "Looking for Python developer"
        )
        
        assert 'ats_score' in result
        assert result['ats_score'] == 85
        assert 'scores' in result
        assert 'strengths' in result
        assert len(result['strengths']) == 3

@pytest.mark.asyncio
async def test_analyze_resume_markdown_removal(gemini_service):
    """Test JSON extraction from markdown code blocks."""
    mock_response = Mock()
    mock_response.text = '''```json
{
    "ats_score": 90,
    "scores": {
        "keyword_match": 90,
        "format_quality": 90,
        "experience_relevance": 90,
        "skills_match": 90,
        "achievements_quantified": 90,
        "overall_presentation": 90
    },
    "strengths": ["Test"],
    "improvements": ["Test"],
    "missing_keywords": [],
    "summary": "Test"
}
```'''
    
    with patch.object(gemini_service.model, 'generate_content', return_value=mock_response):
        result = await gemini_service.analyze_resume("Test resume", "")
        
        assert 'ats_score' in result
        assert result['ats_score'] == 90

@pytest.mark.asyncio
async def test_evaluate_code_valid_input(gemini_service):
    """Test code evaluation with valid input."""
    mock_response = Mock()
    mock_response.text = '''{
        "scores": {
            "correctness": 90,
            "code_quality": 85,
            "efficiency": 80,
            "best_practices": 88
        },
        "overall_score": 87,
        "strengths": ["Clean code", "Good naming"],
        "improvements": ["Add error handling"],
        "time_complexity": "O(n)",
        "space_complexity": "O(1)",
        "feedback": "Well-written solution with good practices."
    }'''
    
    with patch.object(gemini_service.model, 'generate_content', return_value=mock_response):
        result = await gemini_service.evaluate_code(
            "def solution(arr): return sum(arr)",
            "Sum all elements in array",
            ""
        )
        
        assert 'overall_score' in result
        assert result['overall_score'] == 87
        assert 'time_complexity' in result
        assert result['time_complexity'] == "O(n)"

@pytest.mark.asyncio
async def test_analyze_interview_transcript(gemini_service):
    """Test interview transcript analysis."""
    mock_response = Mock()
    mock_response.text = '''{
        "technical_skills_assessment": 85,
        "problem_solving_assessment": 80,
        "answer_quality_scores": [85, 80, 90],
        "confidence_indicators": {
            "tone_confidence": 85,
            "answer_clarity": 88
        },
        "key_strengths": ["Clear communication", "Technical depth"],
        "key_weaknesses": ["Some filler words"],
        "specific_improvements": ["Practice concise answers", "Reduce ums"]
    }'''
    
    with patch.object(gemini_service.model, 'generate_content', return_value=mock_response):
        qa_pairs = [
            {"question": "Tell me about yourself", "answer": "I am a software engineer"}
        ]
        
        result = await gemini_service.analyze_interview_transcript(
            qa_pairs=qa_pairs,
            total_questions=1,
            avg_answer_length=30.0,
            technical_keywords=["software", "engineer"],
            interview_type="technical_software"
        )
        
        assert 'technical_skills_assessment' in result
        assert result['technical_skills_assessment'] == 85
        assert 'confidence_indicators' in result

@pytest.mark.asyncio
async def test_empty_transcript_response(gemini_service):
    """Test empty response when no transcript provided."""
    result = await gemini_service.analyze_interview_transcript(
        qa_pairs=[],
        total_questions=0,
        avg_answer_length=0.0,
        technical_keywords=[],
        interview_type="technical_software"
    )
    
    assert result['technical_skills_assessment'] == 0
    assert result['problem_solving_assessment'] == 0
    assert 'No transcript data available' in result['key_weaknesses']

@pytest.mark.asyncio
async def test_score_clamping(gemini_service):
    """Test that scores are clamped to 0-100 range."""
    mock_response = Mock()
    mock_response.text = '''{
        "technical_skills_assessment": 150,
        "problem_solving_assessment": -10,
        "answer_quality_scores": [200, -50, 75],
        "confidence_indicators": {
            "tone_confidence": 120,
            "answer_clarity": -20
        },
        "key_strengths": [],
        "key_weaknesses": [],
        "specific_improvements": []
    }'''
    
    with patch.object(gemini_service.model, 'generate_content', return_value=mock_response):
        qa_pairs = [{"question": "Test?", "answer": "Test answer"}]
        
        result = await gemini_service.analyze_interview_transcript(
            qa_pairs=qa_pairs,
            total_questions=1,
            avg_answer_length=10.0,
            technical_keywords=[],
            interview_type="technical_software"
        )
        
        # All scores should be clamped to 0-100
        assert 0 <= result['technical_skills_assessment'] <= 100
        assert 0 <= result['problem_solving_assessment'] <= 100
        assert 0 <= result['confidence_indicators']['tone_confidence'] <= 100
        assert 0 <= result['confidence_indicators']['answer_clarity'] <= 100

@pytest.mark.asyncio
async def test_error_handling(gemini_service):
    """Test error handling when API call fails."""
    with patch.object(gemini_service.model, 'generate_content', side_effect=Exception("API Error")):
        with pytest.raises(Exception):
            await gemini_service.analyze_resume("Test resume", "")

def test_initialization_without_api_key():
    """Test that service raises error without API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="GOOGLE_AI_API_KEY is required"):
            GCPGeminiService()
