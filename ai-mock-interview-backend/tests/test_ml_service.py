import pytest
from unittest.mock import Mock, patch
from app.ml_service import InterviewAnalyzer

@pytest.fixture
def analyzer():
    with patch('app.ml_service.OpenAI'):
        return InterviewAnalyzer()

def test_analyze_response_structure(analyzer):
    # Mock the OpenAI client response
    mock_completion = Mock()
    mock_completion.choices = [Mock()]
    mock_completion.choices[0].message.content = '''
    {
        "overall_score": 85,
        "rating": "Good",
        "scores": {
            "content_quality": 80,
            "communication": 90,
            "confidence": 85,
            "technical_accuracy": 85
        },
        "feedback": "Good job",
        "improvements": ["Speak louder"],
        "key_strengths": ["Clear voice"]
    }
    '''
    analyzer.client.chat.completions.create.return_value = mock_completion

    result = analyzer.analyze_response("Test response", "Test question")
    
    assert "overall_score" in result
    assert "rating" in result
    assert "scores" in result
    assert result["overall_score"] == 85
