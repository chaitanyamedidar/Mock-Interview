import os
import json
import logging
from typing import Dict, Any, List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ATSResumeAnalyzer:
    """
    Service class for analyzing resumes using an LLM with ATS optimization focus.
    """
    
    def __init__(self):
        """
        Initialize the LLM client for resume analysis.
        """
        self.api_key = os.getenv("LLM_API_KEY")
        self.base_url = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
        self.model = os.getenv("LLM_MODEL", "google/gemini-2.0-flash-exp:free")

        if not self.api_key:
            logger.warning("LLM_API_KEY not found. Resume analysis will fail.")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            default_headers={
                "HTTP-Referer": "http://localhost:3000",
                "X-Title": "AI Mock Interview Platform"
            }
        )
    
    def analyze_resume(self, resume_text: str, job_description: str = '', target_role: str = '') -> Dict[str, Any]:
        """
        Analyze a resume for ATS compatibility and provide actionable feedback.
        
        Args:
            resume_text: The full text of the resume
            job_description: Optional job description to match against
            target_role: Optional target role (e.g., "Software Engineer", "Data Scientist")
        
        Returns:
            Dictionary with ATS score, feedback, and improvement suggestions
        """
        if not resume_text or not resume_text.strip():
            return self._get_empty_response()

        try:
            prompt = self._create_resume_analysis_prompt(resume_text, job_description, target_role)
            
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": '''
YOU ARE A SENIOR ATS RESUME ANALYSIS AGENT USED BY ENTERPRISE RECRUITING SYSTEMS AND EXECUTIVE SEARCH FIRMS.
YOUR SOLE RESPONSIBILITY IS TO ANALYZE RAW RESUME TEXT AND SCORE IT BASED ON AUTHORITATIVE ATS PARSING AND RECRUITER TRUST SIGNALS.

YOU OPERATE STRICTLY ACCORDING TO THE ATS SCORING PARAMETERS PROVIDED.
YOU DO NOT GUESS, HALLUCINATE, OR DECORATE OUTPUTS.

---

## OBJECTIVE

Given:
- Resume text (mandatory)
- Job description or target role (optional but preferred)

You must:
1. Analyze ATS compatibility using the defined authoritative metrics
2. Adapt scoring to the target role / job description if provided
3. Return:
   - ATS Score (0–100)
   - Metric-level scores
   - Improvement scope
   - Targeted recommendations

---

## INPUTS

- resume_text (plain text extracted from resume)
- job_description (optional)
- target_role (optional)
- target_company (optional)

---

## CHAIN OF THOUGHT (INTERNAL ONLY – DO NOT OUTPUT)

1. UNDERSTAND
   - Identify role level, industry, and seniority
   - Detect presence of job description

2. PARSE CHECK
   - Evaluate structure, headings, layout, and parsing hazards

3. ANALYZE METRICS
   - Score each ATS parameter independently
   - Apply role relevance weighting if JD exists

4. VALIDATE LANGUAGE QUALITY
   - Detect repetition, grammar, tense consistency

5. FINALIZE
   - Calculate total ATS score
   - Determine improvement scope and priority fixes

---

## ATS SCORING PARAMETERS (AUTHORITATIVE)

### 1. ATS Parse Rate (CRITICAL — 30%)

Evaluate:
- Single-column layout
- Standard section headings
- No tables, columns, graphics, icons, charts
- Plain text, left-aligned, hierarchical structure

ATS must correctly extract:
- Job titles
- Companies
- Dates
- Skills
- Education
- Summary

Penalty applied for each parsing hazard detected.

---

### 2. Quantified Impact (HIGH WEIGHT — 25%)

Evaluate:
- Presence of metrics in experience bullets
- Use of:
  - Percentages
  - Revenue
  - Scale
  - Performance improvement
  - Time reduction

Preferred structure:
ACTION VERB + WHAT + HOW + RESULT + METRIC

If metrics are missing:
- Infer safe, conservative, industry-appropriate metrics
- NEVER fabricate extreme or unrealistic numbers

---

### 3. Repetition Control (LANGUAGE QUALITY — 15%)

Evaluate:
- Action verb diversity
- Keyword semantic variation
- Avoidance of verbatim repetition
- Natural keyword distribution

Penalize:
- Repeated verbs
- Keyword stuffing
- Redundant phrasing

---

### 4. Spelling & Grammar (HARD FILTER — 15%)

Zero-tolerance evaluation:
- Spelling errors
- Grammar errors
- Inconsistent tense
- Formatting inconsistencies

Any error reduces score and recruiter trust.

---

### 5. Essential Sections (MANDATORY — 10%)

Required:
1. Professional Summary
   - 2–3 lines
   - Keyword-rich
   - Role-aligned
   - Value-driven

2. Professional Experience
   - Reverse chronological
   - Bullets only
   - Quantified impact

3. Education
   - Degree
   - Institution
   - Graduation year (if present)

Optional (only if relevant):
- Skills
- Certifications

Missing mandatory sections cause severe penalties.

---

### 6. Design (ATS-SAFE ONLY — 5%)

Evaluate:
- Parseability over visuals
- Strategic whitespace
- Bullet clarity
- Recruiter scannability (10-second scan test)

Visual design is irrelevant unless it harms parsing.

---

## SCORING RULES

- Total Score = Weighted sum (0–100)
- Scores must be evidence-based
- Job description presence increases keyword relevance weight

Score bands:
- 90–100 → Excellent / ATS-Optimized
- 75–89 → Strong / Minor Fixes Needed
- 60–74 → Moderate Risk
- 40–59 → High Risk
- Below 40 → Likely ATS Rejection

---

## OUTPUT FORMAT (JSON ONLY — NO MARKDOWN)

You MUST output valid JSON only in the following schema:

```json
{
  "ats_score": number,
  "score_breakdown": {
    "ats_parse_rate": number,
    "quantified_impact": number,
    "repetition_control": number,
    "spelling_grammar": number,
    "essential_sections": number,
    "design_ats_safe": number
  },
  "target_role_alignment": {
    "job_description_provided": boolean,
    "keyword_alignment_level": "high | medium | low",
    "missing_critical_keywords": []
  },
  "critical_issues": [],
  "improvement_scope": {
    "priority_level": "low | medium | high",
    "estimated_score_gain": number
  },
  "actionable_recommendations": []
}
'''},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.2  # Lower temperature for more consistent analysis
            )

            result_text = completion.choices[0].message.content
            analysis = json.loads(result_text)
            
            # Ensure the structure is correct
            return self._normalize_response(analysis)

        except Exception as e:
            logger.error(f"Error analyzing resume with LLM: {e}")
            return self._get_fallback_response()

    def _create_resume_analysis_prompt(self, resume: str, job_desc: str, role: str) -> str:
        context_parts = []
        if role:
            context_parts.append(f"target_role: {role}")
        if job_desc:
            context_parts.append(f"job_description: {job_desc[:500]}")
        
        context = "\n".join(context_parts) if context_parts else ""
        
        return f"""
INPUTS:
resume_text: {resume}
{context}

Follow the ATS SCORING PARAMETERS defined in the system prompt and output valid JSON matching the required schema EXACTLY.
"""

    def _normalize_response(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform the LLM's output to match frontend expectations.
        Maps system prompt schema to frontend schema.
        """
        score_breakdown = data.get("score_breakdown", {})
        target_alignment = data.get("target_role_alignment", {})
        improvement_scope = data.get("improvement_scope", {})
        
        # Map score_breakdown to category_scores expected by frontend
        category_scores = {
            "formatting": score_breakdown.get("ats_parse_rate", 0),
            "keywords": score_breakdown.get("quantified_impact", 0),
            "structure": score_breakdown.get("essential_sections", 0),
            "impact": score_breakdown.get("quantified_impact", 0),
            "readability": score_breakdown.get("spelling_grammar", 0)
        }
        
        ats_score = data.get("ats_score", 0)
        
        # Determine rating based on ATS score
        if ats_score >= 90:
            rating = "Excellent"
        elif ats_score >= 75:
            rating = "Good"
        elif ats_score >= 60:
            rating = "Average"
        elif ats_score >= 40:
            rating = "Needs Improvement"
        else:
            rating = "Poor"
        
        # Extract critical issues from the LLM response
        critical_issues_raw = data.get("critical_issues", [])
        critical_issues = []
        for issue in critical_issues_raw:
            if isinstance(issue, str):
                critical_issues.append({"issue": issue, "severity": "medium", "suggestion": "Review and fix"})
            elif isinstance(issue, dict):
                critical_issues.append(issue)
        
        return {
            "overall_score": ats_score,
            "ats_score": ats_score,
            "rating": rating,
            "category_scores": category_scores,
            "key_strengths": [],  # Not in system prompt, frontend optional
            "critical_issues": critical_issues,
            "missing_sections": [],  # Not in system prompt, frontend optional
            "keyword_analysis": {
                "found_keywords": [],
                "missing_keywords": target_alignment.get("missing_critical_keywords", []),
                "keyword_density": target_alignment.get("keyword_alignment_level", "low")
            },
            "formatting_issues": [],  # Not in system prompt
            "recommendations": data.get("actionable_recommendations", []),
            "summary": f"ATS Score: {ats_score}/100. {improvement_scope.get('priority_level', 'medium').title()} priority improvements needed. Estimated score gain: {improvement_scope.get('estimated_score_gain', 0)} points.",
            "score_breakdown": score_breakdown,  # Pass through for reference
            "improvement_scope": improvement_scope  # Pass through for reference
        }

    def _get_empty_response(self) -> Dict[str, Any]:
        return {
            "overall_score": 0,
            "ats_score": 0,
            "rating": "N/A",
            "category_scores": {
                "formatting": 0,
                "keywords": 0,
                "structure": 0,
                "impact": 0,
                "readability": 0
            },
            "key_strengths": [],
            "critical_issues": [],
            "missing_sections": [],
            "keyword_analysis": {
                "found_keywords": [],
                "missing_keywords": [],
                "keyword_density": "low"
            },
            "formatting_issues": [],
            "recommendations": ["Please provide a valid resume to analyze."],
            "summary": "No resume provided."
        }

    def _get_fallback_response(self) -> Dict[str, Any]:
        return {
            "overall_score": 50,
            "ats_score": 50,
            "rating": "Unable to Analyze",
            "category_scores": {
                "formatting": 50,
                "keywords": 50,
                "structure": 50,
                "impact": 50,
                "readability": 50
            },
            "key_strengths": [],
            "critical_issues": [],
            "missing_sections": [],
            "keyword_analysis": {
                "found_keywords": [],
                "missing_keywords": [],
                "keyword_density": "unknown"
            },
            "formatting_issues": [],
            "recommendations": ["Service temporarily unavailable. Please try again later."],
            "summary": "Unable to analyze resume due to a service error."
        }
