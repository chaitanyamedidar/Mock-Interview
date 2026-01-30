import os
import json
import re
import logging
import asyncio
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class GCPGeminiService:
    """
    Service class for interacting with Google Cloud Platform Gemini API.
    Provides methods for resume analysis, code evaluation, and interview transcript analysis.
    Uses native google-generativeai SDK for production-grade reliability.
    """
    
    def __init__(self):
        """Initialize the GCP Gemini client with configuration."""
        self.api_key = os.getenv("GOOGLE_AI_API_KEY")
        
        if not self.api_key:
            logger.warning("GOOGLE_AI_API_KEY not found. GCP Gemini will not be available.")
            raise ValueError("GOOGLE_AI_API_KEY is required for GCP Gemini service")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model with generation config
        self.model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.generation_config = {
            "temperature": float(os.getenv("GEMINI_TEMPERATURE", "0.3")),
            "top_p": float(os.getenv("GEMINI_TOP_P", "0.95")),
            "top_k": int(os.getenv("GEMINI_TOP_K", "40")),
            "max_output_tokens": int(os.getenv("GEMINI_MAX_TOKENS", "4096")),  # Increased for longer responses
        }
        
        self.model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config=self.generation_config
        )
        
        logger.info(f"GCP Gemini service initialized with model: {self.model_name}")
    
    async def analyze_resume(
        self, 
        resume_text: str, 
        job_description: str = ""
    ) -> Dict[str, Any]:
        """
        Analyze resume for ATS compatibility and scoring.
        
        Args:
            resume_text: Full text of the resume (truncated to 4000 chars)
            job_description: Optional job description to match against (truncated to 1000 chars)
        
        Returns:
            Dictionary with ATS score, category scores, strengths, improvements, and summary
        
        Raises:
            Exception: If API call fails or JSON parsing fails
        """
        # Truncate inputs to prevent token limit issues
        resume_text = resume_text[:4000] if resume_text else ""
        job_description = job_description[:1000] if job_description else ""
        
        if not resume_text.strip():
            raise ValueError("Resume text cannot be empty")
        
        prompt = self._create_resume_prompt(resume_text, job_description)
        
        try:
            # Make async API call
            response = await self._generate_content_async(prompt)
            result = self._parse_json_response(response.text)
            
            # Validate resume analysis schema
            self._validate_resume_response(result)
            
            logger.info(f"Resume analysis completed. ATS Score: {result.get('ats_score', 'N/A')}")
            return result
        
        except Exception as e:
            logger.error(f"Resume analysis failed: {e}")
            raise
    
    async def evaluate_code(
        self,
        code: str,
        question: str,
        expected_approach: str = ""
    ) -> Dict[str, Any]:
        """
        Evaluate technical interview code solution.
        
        Args:
            code: User's code solution (preserves formatting)
            question: The interview question text
            expected_approach: Optional expected solution approach
        
        Returns:
            Dictionary with scores, complexity analysis, strengths, improvements, and feedback
        
        Raises:
            Exception: If API call fails or JSON parsing fails
        """
        if not code.strip() or not question.strip():
            raise ValueError("Code and question cannot be empty")
        
        prompt = self._create_code_eval_prompt(code, question, expected_approach)
        
        try:
            response = await self._generate_content_async(prompt)
            result = self._parse_json_response(response.text)
            
            # Validate code evaluation schema
            self._validate_code_response(result)
            
            logger.info(f"Code evaluation completed. Overall Score: {result.get('overall_score', 'N/A')}")
            return result
        
        except Exception as e:
            logger.error(f"Code evaluation failed: {e}")
            raise
    
    async def analyze_interview_transcript(
        self,
        qa_pairs: List[Dict[str, str]],
        total_questions: int,
        avg_answer_length: float,
        technical_keywords: List[str],
        interview_type: str
    ) -> Dict[str, Any]:
        """
        Analyze interview transcript for tone, coherence, and technical depth.
        
        Args:
            qa_pairs: List of {"question": str, "answer": str} dictionaries
            total_questions: Total number of questions in interview
            avg_answer_length: Average answer length in seconds
            technical_keywords: List of technical keywords detected
            interview_type: Type of interview (technical_software, behavioral, etc.)
        
        Returns:
            Dictionary with LLM assessment scores and recommendations
        
        Raises:
            Exception: If API call fails or JSON parsing fails
        """
        if not qa_pairs:
            return self._get_empty_transcript_response()
        
        prompt = self._create_transcript_prompt(
            qa_pairs,
            total_questions,
            avg_answer_length,
            technical_keywords,
            interview_type
        )
        
        try:
            response = await self._generate_content_async(prompt)
            result = self._parse_json_response(response.text)
            
            # Validate and normalize response
            validated = self._validate_transcript_response(result)
            
            logger.info(f"Interview transcript analysis completed for {len(qa_pairs)} Q&A pairs")
            return validated
        
        except Exception as e:
            logger.error(f"Interview transcript analysis failed: {e}")
            return self._get_fallback_transcript_response()
    
    async def _generate_content_async(self, prompt: str, retry_count: int = 1) -> Any:
        """
        Generate content with retry logic for rate limits.
        
        Args:
            prompt: The prompt to send to the model
            retry_count: Number of retries on rate limit (default: 1)
        
        Returns:
            Response object from Gemini API
        """
        for attempt in range(retry_count + 1):
            try:
                # Use synchronous call wrapped in executor for async compatibility
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    self.model.generate_content,
                    prompt
                )
                return response
            
            except Exception as e:
                error_str = str(e).lower()
                
                # Check for rate limit errors
                if "429" in error_str or "rate limit" in error_str or "quota" in error_str:
                    if attempt < retry_count:
                        wait_time = 2 ** attempt  # Exponential backoff
                        logger.warning(f"Rate limit hit, retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                        continue
                
                # Re-raise on final attempt or non-rate-limit errors
                raise
    
    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """
        Parse JSON from response, handling markdown code blocks and malformed JSON.
        
        Args:
            text: Raw response text from Gemini
        
        Returns:
            Parsed JSON dictionary
        
        Raises:
            json.JSONDecodeError: If JSON parsing fails after all cleanup attempts
        """
        original_text = text
        
        # Remove markdown code blocks more aggressively
        # Handle ```json\n{...}\n``` format
        text = re.sub(r'^```json\s*\n?', '', text, flags=re.MULTILINE)
        text = re.sub(r'\n?```\s*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^```\s*\n?', '', text, flags=re.MULTILINE)
        text = text.strip()
        
        # Try parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}")
            
            # Try aggressive cleanup
            try:
                # Remove ALL occurrences of ``` 
                cleaned = text.replace('```json', '').replace('```', '').strip()
                
                # Try to extract JSON object - need to find matching braces
                start_idx = cleaned.find('{')
                
                if start_idx == -1:
                    raise ValueError("No JSON object found in response")
                
                # Find the matching closing brace by counting braces
                brace_count = 0
                end_idx = -1
                for i in range(start_idx, len(cleaned)):
                    if cleaned[i] == '{':
                        brace_count += 1
                    elif cleaned[i] == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_idx = i
                            break
                
                if end_idx == -1:
                    raise ValueError("No matching closing brace found")
                
                json_str = cleaned[start_idx:end_idx+1]
                logger.info(f"Extracted JSON from position {start_idx} to {end_idx} ({len(json_str)} chars)")
                return json.loads(json_str)
                    
            except (json.JSONDecodeError, ValueError) as e2:
                logger.error(f"JSON parse error after cleanup: {e2}")
                logger.error(f"Original response (first 1000 chars): {original_text[:1000]}")
                raise json.JSONDecodeError(
                    f"Failed to parse JSON response: {str(e)}",
                    original_text[:100],
                    0
                )
    
    # ==================== PROMPT CREATION METHODS ====================
    
    def _create_resume_prompt(self, resume_text: str, job_description: str) -> str:
        """Create prompt for resume analysis."""
        jd_section = f"\n\nJOB DESCRIPTION:\n{job_description}" if job_description else ""
        
        return f"""You are an expert ATS resume analyzer. Analyze this resume and return ONLY valid JSON.

RESUME:
{resume_text}{jd_section}

Return ONLY a JSON object (no markdown, no explanations) with this exact structure:
{{
  "ats_score": <number 0-100>,
  "scores": {{
    "keyword_match": <number 0-100>,
    "format_quality": <number 0-100>,
    "experience_relevance": <number 0-100>,
    "skills_match": <number 0-100>,
    "achievements_quantified": <number 0-100>,
    "overall_presentation": <number 0-100>
  }},
  "strengths": ["strength 1", "strength 2", "strength 3"],
  "improvements": ["improvement 1", "improvement 2", "improvement 3"],
  "missing_keywords": ["keyword 1", "keyword 2"],
  "summary": "Brief 2-3 sentence summary"
}}

Scoring: 90-100=Excellent, 80-89=Strong, 70-79=Good, 60-69=Average, <60=Needs work."""
    
    def _create_code_eval_prompt(self, code: str, question: str, expected_approach: str) -> str:
        """Create prompt for code evaluation."""
        approach_section = f"\n\nEXPECTED APPROACH:\n{expected_approach}" if expected_approach else ""
        
        return f"""You are an expert technical interviewer evaluating a coding solution.

QUESTION:
{question}

USER'S CODE:
```
{code}
```{approach_section}

Evaluate the code solution and return ONLY valid JSON (no markdown, no code blocks) with this exact schema:

{{
  "scores": {{
    "correctness": <number 0-100>,
    "code_quality": <number 0-100>,
    "efficiency": <number 0-100>,
    "best_practices": <number 0-100>
  }},
  "overall_score": <number 0-100>,
  "strengths": ["<string>", "<string>"],
  "improvements": ["<string>", "<string>"],
  "time_complexity": "<Big O notation>",
  "space_complexity": "<Big O notation>",
  "feedback": "<2-3 sentence summary>"
}}

Scoring guidelines:
- Correctness: Does it solve the problem correctly?
- Code Quality: Readability, naming, structure
- Efficiency: Time and space complexity
- Best Practices: Error handling, edge cases, coding standards

Overall score should be weighted average: correctness (40%), quality (25%), efficiency (25%), best practices (10%)."""
    
    def _create_transcript_prompt(
        self,
        qa_pairs: List[Dict[str, str]],
        total_questions: int,
        avg_answer_length: float,
        technical_keywords: List[str],
        interview_type: str
    ) -> str:
        """Create prompt for interview transcript analysis."""
        # Format Q&A pairs
        qa_formatted = ""
        for i, qa in enumerate(qa_pairs, 1):
            qa_formatted += f"\nQ{i}: {qa['question']}\n"
            qa_formatted += f"A{i}: {qa['answer']}\n"
        
        keyword_list = ", ".join(technical_keywords) if technical_keywords else "None detected"
        
        return f"""You are an expert interview coach analyzing mock interview transcripts.

Your role is to assess aspects that require human-like judgment:
- Technical skills and knowledge depth
- Problem-solving approach and clarity
- Answer quality and relevance
- Confidence and communication tone
- Specific strengths and areas for improvement

TRANSCRIPT:
{qa_formatted}

CONTEXT:
- Total questions: {total_questions}
- Average answer length: {avg_answer_length:.1f} seconds
- Technical keywords used: {keyword_list}
- Interview type: {interview_type}

Return ONLY valid JSON (no markdown, no code blocks) with this exact schema:

{{
  "technical_skills_assessment": <number 0-100>,
  "problem_solving_assessment": <number 0-100>,
  "confidence_indicators": {{
    "tone_confidence": <number 0-100>,
    "answer_clarity": <number 0-100>
  }},
  "per_question_analysis": [
    {{
      "question_id": <int index>,
      "score": <number 0-100>,
      "key_strengths": ["<string>", "<string>"],
      "improvements": ["<string>", "<string>"]
    }}
  ],
  "key_strengths": ["<string>", "<string>", "<string>"],
  "key_weaknesses": ["<string>", "<string>", "<string>"],
  "specific_improvements": ["<string>", "<string>", "<string>"]
}}

Scoring guidelines:
- 90-100: Excellent, professional-level
- 80-89: Strong, minor improvements needed
- 70-79: Good, some gaps to address
- 60-69: Average, significant improvement needed
- Below 60: Needs substantial work

Be specific in strengths/weaknesses/improvements. Reference actual answers when possible.
Provide actionable, concrete recommendations."""
    
    # ==================== VALIDATION METHODS ====================
    
    def _validate_resume_response(self, data: Dict[str, Any]) -> None:
        """Validate resume analysis response schema."""
        required_fields = ["ats_score", "scores", "strengths", "improvements", "summary"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate scores object
        score_fields = ["keyword_match", "format_quality", "experience_relevance", 
                       "skills_match", "achievements_quantified", "overall_presentation"]
        for field in score_fields:
            if field not in data["scores"]:
                raise ValueError(f"Missing score field: {field}")
    
    def _validate_code_response(self, data: Dict[str, Any]) -> None:
        """Validate code evaluation response schema."""
        required_fields = ["scores", "overall_score", "strengths", "improvements", 
                          "time_complexity", "space_complexity", "feedback"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate scores object
        score_fields = ["correctness", "code_quality", "efficiency", "best_practices"]
        for field in score_fields:
            if field not in data["scores"]:
                raise ValueError(f"Missing score field: {field}")
    
    def _validate_transcript_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize interview transcript response."""
        # Ensure all required fields exist with defaults
        # Validate per_question_analysis
        per_question = data.get("per_question_analysis", [])
        validated_questions = []
        for q in per_question:
            validated_questions.append({
                "question_id": q.get("question_id", 0),
                "score": self._clamp_score(q.get("score", 50)),
                "key_strengths": q.get("key_strengths", [])[:2],
                "improvements": q.get("improvements", [])[:2]
            })

        validated = {
            "technical_skills_assessment": self._clamp_score(data.get("technical_skills_assessment", 50)),
            "problem_solving_assessment": self._clamp_score(data.get("problem_solving_assessment", 50)),
            "per_question_analysis": validated_questions,
            "confidence_indicators": {
                "tone_confidence": self._clamp_score(
                    data.get("confidence_indicators", {}).get("tone_confidence", 50)
                ),
                "answer_clarity": self._clamp_score(
                    data.get("confidence_indicators", {}).get("answer_clarity", 50)
                )
            },
            "key_strengths": data.get("key_strengths", [])[:3],  # Limit to 3
            "key_weaknesses": data.get("key_weaknesses", [])[:3],  # Limit to 3
            "specific_improvements": data.get("specific_improvements", [])[:5]  # Limit to 5
        }
        
        return validated
    
    def _clamp_score(self, score: Any) -> float:
        """Clamp score to 0-100 range."""
        try:
            score_float = float(score)
            return max(0.0, min(100.0, score_float))
        except (TypeError, ValueError):
            return 50.0  # Default to middle score if invalid
    
    # ==================== FALLBACK RESPONSES ====================
    
    def _get_empty_transcript_response(self) -> Dict[str, Any]:
        """Return empty response when no transcript provided."""
        return {
            "technical_skills_assessment": 0,
            "problem_solving_assessment": 0,
            "answer_quality_scores": [],
            "confidence_indicators": {
                "tone_confidence": 0,
                "answer_clarity": 0
            },
            "key_strengths": [],
            "key_weaknesses": ["No transcript data available"],
            "specific_improvements": ["Complete interview questions to receive feedback"]
        }
    
    def _get_fallback_transcript_response(self) -> Dict[str, Any]:
        """Return fallback response when LLM analysis fails."""
        return {
            "technical_skills_assessment": 50,
            "problem_solving_assessment": 50,
            "answer_quality_scores": [],
            "confidence_indicators": {
                "tone_confidence": 50,
                "answer_clarity": 50
            },
            "key_strengths": [],
            "key_weaknesses": [],
            "specific_improvements": ["LLM analysis temporarily unavailable - scores based on rule-based analysis only"]
        }
