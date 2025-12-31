import os
import json
import logging
from typing import Dict, Any, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class InterviewAnalyzer:
    """
    Service class for analyzing interview responses using an LLM (via OpenRouter/OpenAI).
    """
    
    def __init__(self):
        """
        Initialize the LLM client.
        """
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp:free") # Default to Gemini 2.0 Flash Experimental (free)

        if not self.api_key:
            logger.warning("LLM_API_KEY not found. Analysis will fail.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "AI Mock Interview Platform"
            }
        )
    
    def analyze_response(self, response_text: str, question_text: str = '', interview_type: str = 'technical_software') -> Dict[str, Any]:
        """
        Analyze a single interview response using the LLM.
        """
        if not response_text or not response_text.strip():
            return self._get_empty_response()

        try:
            prompt = self._create_analysis_prompt(response_text, question_text, interview_type)
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer. Analyze the candidate's response and provide structured feedback in JSON format."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )

            result_text = completion.choices[0].message.content
            analysis = json.loads(result_text)
            
            # Ensure the structure matches what the frontend expects
            return self._normalize_response(analysis, interview_type)

        except Exception as e:
            logger.error(f"Error analyzing response with LLM: {e}")
            return self._get_fallback_response()

    def _create_analysis_prompt(self, response: str, question: str, type: str) -> str:
        return f"""
        Analyze the following interview response.
        
        Context:
        - Interview Type: {type}
        - Question: {question}
        - Candidate Response: "{response}"

        Provide a JSON output with the following fields:
        1. overall_score (0-100 float)
        2. rating (one of: "Excellent", "Good", "Average", "Needs Improvement", "Poor")
        3. scores (object with 0-100 scores for: content_quality, communication, confidence, technical_accuracy)
        4. feedback (string, brief constructive feedback)
        5. improvements (list of strings, specific actionable tips)
        6. key_strengths (list of strings)

        Ensure the JSON is valid.
        """

    def _normalize_response(self, data: Dict[str, Any], interview_type: str) -> Dict[str, Any]:
        """
        Ensure the LLM response has all required fields for the frontend.
        """
        default_scores = {
            "content_quality": 0,
            "communication": 0,
            "confidence": 0,
            "technical_accuracy": 0
        }
        
        return {
            "overall_score": data.get("overall_score", 0),
            "rating": data.get("rating", "Needs Improvement"),
            "scores": {**default_scores, **data.get("scores", {})},
            "feedback": data.get("feedback", "No feedback provided."),
            "improvements": data.get("improvements", []),
            "key_strengths": data.get("key_strengths", []),
            "interview_type": interview_type,
            "ml_prediction": {"confidence": 1.0, "prediction": data.get("rating", "Average")} # Mock for backward compatibility
        }

    def _get_empty_response(self) -> Dict[str, Any]:
        return {
            "overall_score": 0,
            "rating": "N/A",
            "scores": {"content_quality": 0, "communication": 0, "confidence": 0, "technical_accuracy": 0},
            "feedback": "No response detected.",
            "improvements": [],
            "key_strengths": [],
            "interview_type": "unknown"
        }

    def _get_fallback_response(self) -> Dict[str, Any]:
        return {
            "overall_score": 50,
            "rating": "Average",
            "scores": {"content_quality": 50, "communication": 50, "confidence": 50, "technical_accuracy": 50},
            "feedback": "Unable to analyze response at this time due to a service error.",
            "improvements": ["Please try again later."],
            "key_strengths": [],
            "interview_type": "unknown"
        }
