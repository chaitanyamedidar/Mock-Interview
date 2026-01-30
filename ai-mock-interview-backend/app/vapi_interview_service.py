import re
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from .gcp_gemini_service import GCPGeminiService
from .models import InterviewReport

logger = logging.getLogger(__name__)

class VAPIInterviewAnalyzer:
    """
    Service for analyzing VAPI interview transcripts.
    Combines rule-based analysis with LLM assessment.
    """
    
    def __init__(self):
        """Initialize the analyzer with Gemini service."""
        self.gemini_service = GCPGeminiService()
        
        # Filler words to detect
        self.filler_words = [
            'um', 'uh', 'like', 'you know', 'sort of', 'kind of',
            'actually', 'basically', 'literally', 'i mean'
        ]
        
        # Technical keywords by domain
        self.technical_keywords = {
            'technical_software': [
                'algorithm', 'data structure', 'complexity', 'optimization',
                'api', 'database', 'sql', 'nosql', 'rest', 'graphql',
                'microservices', 'architecture', 'design pattern', 'oop',
                'testing', 'debugging', 'git', 'version control',
                'framework', 'library', 'async', 'concurrent', 'thread',
                'cache', 'performance', 'scalability', 'security'
            ],
            'behavioral': [
                'team', 'collaboration', 'leadership', 'conflict',
                'challenge', 'solution', 'result', 'impact', 'stakeholder',
                'communication', 'deadline', 'priority', 'feedback'
            ],
            'system_design': [
                'scalability', 'load balancer', 'cache', 'cdn', 'database',
                'sharding', 'replication', 'consistency', 'availability',
                'partition', 'microservices', 'monolith', 'queue', 'pub/sub',
                'latency', 'throughput', 'bottleneck', 'trade-off'
            ]
        }
    
    async def process_interview_transcript(
        self,
        vapi_payload: Dict[str, Any],
        db: Session
    ) -> Dict[str, Any]:
        """
        Process complete VAPI webhook payload and generate analysis.
        
        Args:
            vapi_payload: VAPI webhook payload with transcript
            db: Database session for querying previous reports
        
        Returns:
            Complete analysis matching frontend schema
        """
        start_time = datetime.utcnow()
        
        # Extract data from payload
        call_data = vapi_payload.get('call', {})
        call_id = call_data.get('id')
        call_duration = call_data.get('duration', 0)
        metadata = call_data.get('metadata', {})
        session_id = metadata.get('session_id')
        user_id = metadata.get('user_id')  # Optional
        
        transcript_data = call_data.get('transcript', {})
        messages = transcript_data.get('messages', [])
        
        # Extract Q&A pairs
        qa_pairs = self.extract_qa_pairs(messages)
        total_questions = len(qa_pairs)
        
        if total_questions == 0:
            raise ValueError("No questions found in transcript")
        
        # Rule-based analysis
        communication_score = self.calculate_communication_score(qa_pairs, call_duration)
        time_management_score = self.calculate_time_management_score(qa_pairs, call_duration, total_questions)
        
        # Detect technical keywords
        interview_type = metadata.get('interview_type', 'technical_software')
        detected_keywords = self.detect_technical_keywords(qa_pairs, interview_type)
        keyword_score = min(100, len(detected_keywords) * 10)  # 10 points per keyword, max 100
        
        # Calculate answer durations
        answer_durations = self.calculate_answer_durations(messages)
        avg_answer_length = sum(answer_durations) / len(answer_durations) if answer_durations else 0
        
        # LLM analysis (async call)
        llm_analysis = await self.gemini_service.analyze_interview_transcript(
            qa_pairs=qa_pairs,
            total_questions=total_questions,
            avg_answer_length=avg_answer_length,
            technical_keywords=detected_keywords,
            interview_type=interview_type
        )
        
        # Combine scores
        technical_skills_score = (keyword_score * 0.4) + (llm_analysis['technical_skills_assessment'] * 0.6)
        problem_solving_score = llm_analysis['problem_solving_assessment']
        
        # Calculate overall score (weighted average)
        overall_score = (
            communication_score * 0.25 +
            technical_skills_score * 0.30 +
            problem_solving_score * 0.30 +
            time_management_score * 0.15
        )
        
        # Determine performance label
        performance_label = self.get_performance_label(overall_score)
        
        # Calculate trends
        trends = self.calculate_trends(db, user_id, session_id, {
            'communication': communication_score,
            'technical_skills': technical_skills_score,
            'problem_solving': problem_solving_score,
            'time_management': time_management_score
        })
        
        # Generate recommendations
        recommendations = self.generate_recommendations(
            llm_analysis,
            communication_score,
            technical_skills_score,
            problem_solving_score,
            time_management_score
        )
        
        # Build response
        processing_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        
        response = {
            'report_summary': {
                'overall_score': round(overall_score, 2),
                'performance_label': performance_label,
                'total_questions_analyzed': total_questions,
                'categories': {
                    'communication': {
                        'score': round(communication_score, 2),
                        'trend': trends['communication']
                    },
                    'technical_skills': {
                        'score': round(technical_skills_score, 2),
                        'trend': trends['technical_skills']
                    },
                    'problem_solving': {
                        'score': round(problem_solving_score, 2),
                        'trend': trends['problem_solving']
                    },
                    'time_management': {
                        'score': round(time_management_score, 2),
                        'trend': trends['time_management']
                    }
                }
            },
            'ai_recommendations': recommendations,
            'metadata': {
                'session_id': session_id,
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'processing_time_ms': processing_time_ms
            }
        }
        
        # Combine Q&A with LLM feedback
        analyzed_transcript = []
        per_question_analysis = llm_analysis.get('per_question_analysis', [])
        
        for i, qa in enumerate(qa_pairs):
            # Find matching analysis or use defaults
            analysis = next((item for item in per_question_analysis if item.get('question_index', i+1) == i+1), {})
            if not analysis and i < len(per_question_analysis):
                # Fallback to positional match if index missing
                analysis = per_question_analysis[i]
                
            analyzed_transcript.append({
                "question": qa['question'],
                "answer": qa['answer'],
                "score": analysis.get('score', 70),
                "strengths": analysis.get('key_strengths', []),
                "improvements": analysis.get('improvements', []),
                "timestamp": messages[0].get('timestamp') if messages else None # Approximation
            })

        # Save to database
        self.save_report(
            db=db,
            session_id=session_id,
            user_id=user_id,
            call_id=call_id,
            call_duration=call_duration,
            overall_score=overall_score,
            performance_label=performance_label,
            total_questions=total_questions,
            category_scores=response['report_summary']['categories'],
            recommendations=recommendations,
            transcript=analyzed_transcript, # Saving enrichment transcript instead of raw messages
            processing_time_ms=processing_time_ms
        )
        
        return response
    
    def extract_qa_pairs(self, messages: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract question-answer pairs from VAPI transcript messages."""
        qa_pairs = []
        current_question = None
        
        for msg in messages:
            role = msg.get('role', '')
            text = msg.get('message', '')
            
            if role == 'assistant':
                # This is a question
                current_question = text
            elif role == 'user' and current_question:
                # This is an answer to the previous question
                qa_pairs.append({
                    'question': current_question,
                    'answer': text
                })
                current_question = None
        
        return qa_pairs
    
    def calculate_communication_score(self, qa_pairs: List[Dict[str, str]], call_duration: int) -> float:
        """
        Calculate communication score based on filler words, pauses, and speaking time.
        Base score: 70, adjustments based on metrics.
        """
        score = 70.0
        total_answer_text = ' '.join([qa['answer'] for qa in qa_pairs])
        total_words = len(total_answer_text.split())
        
        # Count filler words
        filler_count = 0
        for filler in self.filler_words:
            pattern = r'\b' + re.escape(filler) + r'\b'
            filler_count += len(re.findall(pattern, total_answer_text.lower()))
        
        # Adjust for filler words (-3 per filler word)
        score -= (filler_count * 3)
        
        # Estimate speaking time (assuming ~150 words per minute)
        estimated_speaking_time = (total_words / 150) * 60  # in seconds
        speaking_ratio = estimated_speaking_time / call_duration if call_duration > 0 else 0
        
        # Bonus if speaking time > 50% of call duration
        if speaking_ratio > 0.5:
            score += 10
        
        # Check for optimal answer lengths (30-120 seconds)
        for qa in qa_pairs:
            word_count = len(qa['answer'].split())
            estimated_duration = (word_count / 150) * 60
            if 30 <= estimated_duration <= 120:
                score += 5
        
        # Detect long pauses (multiple consecutive periods or "...")
        pause_pattern = r'\.{3,}|\.\s+\.\s+\.'
        long_pauses = len(re.findall(pause_pattern, total_answer_text))
        score -= (long_pauses * 5)
        
        return max(0.0, min(100.0, score))
    
    def calculate_time_management_score(
        self, 
        qa_pairs: List[Dict[str, str]], 
        call_duration: int,
        total_questions: int
    ) -> float:
        """
        Calculate time management score based on answer lengths and completion.
        Base score: 75, adjustments based on metrics.
        """
        score = 75.0
        
        # Bonus for answering all questions
        if len(qa_pairs) == total_questions:
            score += 10
        else:
            # Penalty for skipped questions
            skipped = total_questions - len(qa_pairs)
            score -= (skipped * 5)
        
        # Check for overly long answers (>180 seconds / ~450 words)
        for qa in qa_pairs:
            word_count = len(qa['answer'].split())
            estimated_duration = (word_count / 150) * 60
            if estimated_duration > 180:
                score -= 10
        
        # Bonus for optimal call duration (15-25 minutes for 5 questions)
        expected_duration = total_questions * 5 * 60  # 5 minutes per question
        if 0.75 * expected_duration <= call_duration <= 1.25 * expected_duration:
            score += 5
        
        return max(0.0, min(100.0, score))
    
    def detect_technical_keywords(
        self, 
        qa_pairs: List[Dict[str, str]], 
        interview_type: str
    ) -> List[str]:
        """Detect technical keywords in answers based on interview type."""
        keywords = self.technical_keywords.get(interview_type, self.technical_keywords['technical_software'])
        total_answer_text = ' '.join([qa['answer'] for qa in qa_pairs]).lower()
        
        detected = []
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, total_answer_text):
                detected.append(keyword)
        
        return detected
    
    def calculate_answer_durations(self, messages: List[Dict[str, Any]]) -> List[float]:
        """Calculate duration of each answer based on timestamps."""
        durations = []
        
        for i in range(len(messages) - 1):
            if messages[i].get('role') == 'user':
                # User answer
                try:
                    start_time = datetime.fromisoformat(messages[i].get('timestamp', '').replace('Z', '+00:00'))
                    end_time = datetime.fromisoformat(messages[i + 1].get('timestamp', '').replace('Z', '+00:00'))
                    duration = (end_time - start_time).total_seconds()
                    durations.append(duration)
                except (ValueError, AttributeError):
                    continue
        
        return durations
    
    def get_performance_label(self, overall_score: float) -> str:
        """Determine performance label based on overall score."""
        if overall_score >= 90:
            return "Excellent"
        elif overall_score >= 80:
            return "Strong Performance"
        elif overall_score >= 70:
            return "Good"
        elif overall_score >= 60:
            return "Average"
        else:
            return "Needs Improvement"
    
    def calculate_trends(
        self,
        db: Session,
        user_id: Optional[int],
        current_session_id: str,
        current_scores: Dict[str, float]
    ) -> Dict[str, str]:
        """Calculate trends by comparing to previous interview."""
        trends = {
            'communication': 'stable',
            'technical_skills': 'stable',
            'problem_solving': 'stable',
            'time_management': 'stable'
        }
        
        if not user_id:
            return trends
        
        # Query previous report for this user
        previous_report = db.query(InterviewReport).filter(
            InterviewReport.user_id == user_id,
            InterviewReport.session_id != current_session_id
        ).order_by(InterviewReport.created_at.desc()).first()
        
        if not previous_report:
            return trends
        
        # Compare scores
        previous_scores = previous_report.category_scores
        for category in trends.keys():
            current = current_scores[category]
            previous = previous_scores.get(category, {}).get('score', current)
            
            if current > previous + 5:
                trends[category] = 'up'
            elif current < previous - 5:
                trends[category] = 'down'
        
        return trends
    
    def generate_recommendations(
        self,
        llm_analysis: Dict[str, Any],
        communication_score: float,
        technical_skills_score: float,
        problem_solving_score: float,
        time_management_score: float
    ) -> List[Dict[str, str]]:
        """Generate recommendations combining LLM suggestions and score-based tips."""
        recommendations = []
        
        # Add LLM-specific improvements first (highest priority)
        llm_improvements = llm_analysis.get('specific_improvements', [])
        for improvement in llm_improvements[:3]:  # Max 3 from LLM
            recommendations.append({
                'title': 'Personalized Feedback',
                'description': improvement
            })
        
        # Add generic recommendations based on low scores
        if communication_score < 70:
            recommendations.append({
                'title': 'Reduce Filler Words',
                'description': 'Practice pausing instead of using filler words like "um", "uh", and "like". Record yourself and listen back to identify patterns.'
            })
        
        if technical_skills_score < 70:
            recommendations.append({
                'title': 'Strengthen Technical Knowledge',
                'description': 'Review core technical concepts and practice explaining them clearly. Use specific terminology and examples from your experience.'
            })
        
        if problem_solving_score < 70:
            recommendations.append({
                'title': 'Practice STAR Method',
                'description': 'Structure your answers using Situation, Task, Action, Result. This helps you provide complete, organized responses.'
            })
        
        if time_management_score < 70:
            recommendations.append({
                'title': 'Practice Concise Answers',
                'description': 'Aim for 1-2 minute answers. Practice summarizing key points without losing important details.'
            })
        
        # Limit to 5 recommendations total
        return recommendations[:5]
    
    def save_report(
        self,
        db: Session,
        session_id: str,
        user_id: Optional[int],
        call_id: str,
        call_duration: int,
        overall_score: float,
        performance_label: str,
        total_questions: int,
        category_scores: Dict[str, Any],
        recommendations: List[Dict[str, str]],
        transcript: List[Dict[str, Any]],
        processing_time_ms: int
    ) -> None:
        """Save interview report to database."""
        try:
            report = InterviewReport(
                session_id=session_id,
                user_id=user_id,
                call_id=call_id,
                overall_score=overall_score,
                performance_label=performance_label,
                total_questions_analyzed=total_questions,
                category_scores=category_scores,
                recommendations=recommendations,
                transcript=transcript,
                processing_time_ms=processing_time_ms,
                call_duration_seconds=call_duration
            )
            
            db.add(report)
            db.commit()
            logger.info(f"Saved interview report for session {session_id}")
        
        except Exception as e:
            logger.error(f"Failed to save interview report: {e}")
            db.rollback()
            # Don't raise - we still want to return the response to user
