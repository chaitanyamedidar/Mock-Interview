from fastapi import FastAPI, HTTPException, Depends, status, Request, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import asyncio
import logging
from sqlalchemy.orm import Session

# Import custom modules
from .database import get_db, SessionLocal, init_database
from .models import InterviewSession, SessionResponse, FeedbackDetail, InterviewQuestion
from .ml_service import InterviewAnalyzer
from .vapi_service import VAPIManager
from .resume_service import ATSResumeAnalyzer
from .file_parser import FileParser
from .file_parser import FileParser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Mock Interview API",
    description="Backend API for AI-powered mock interview platform with VAPI integration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = InterviewAnalyzer()
vapi_manager = VAPIManager()
resume_analyzer = ATSResumeAnalyzer()

# Pydantic models for request/response validation
class InterviewStartRequest(BaseModel):
    interview_type: str = Field(..., description="Type of interview (technical_software, behavioral, etc.)")
    difficulty: str = Field(..., description="Difficulty level (entry, intermediate, advanced)")
    duration: int = Field(..., description="Duration in minutes", ge=10, le=120)
    company: Optional[str] = Field(None, description="Specific company (optional)")

class InterviewStartResponse(BaseModel):
    session_id: str
    questions: List[Dict[str, Any]]
    vapi_config: Dict[str, Any]
    assistant_id: Optional[str] = None

class ResponseAnalysisRequest(BaseModel):
    session_id: str
    response_text: str
    question_id: int
    question_number: int

class ResponseAnalysisResult(BaseModel):
    response_id: int
    quality_score: float
    content_quality: float
    communication: float
    confidence: float
    technical_accuracy: float
    rating: str
    feedback: List[Dict[str, str]]
    metrics: Dict[str, Any]

class EndInterviewRequest(BaseModel):
    session_id: str

class FeedbackResponse(BaseModel):
    session_id: str
    overall_score: float
    overall_rating: str
    strengths: List[str]
    improvements: List[str]
    detailed_analysis: Dict[str, Any]
    question_breakdown: List[Dict[str, Any]]

class QuestionResponse(BaseModel):
    questions: List[Dict[str, Any]]
    count: int

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    try:
        init_database()
        from .database import seed_questions
        seed_questions()
        logger.info("Database initialized and seeded successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "AI Mock Interview API",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "services": {
            "database": "connected",
            "ml_model": "loaded" if analyzer.model else "rule_based",
            "vapi": "configured" if vapi_manager.api_key else "not_configured"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Interview Management Endpoints
@app.post("/api/interview/start", response_model=InterviewStartResponse)
async def start_interview(request: InterviewStartRequest, db: Session = Depends(get_db)):
    """
    Start a new interview session with VAPI integration
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Get questions based on filters
        questions = get_questions_for_interview(
            interview_type=request.interview_type,
            difficulty=request.difficulty,
            company=request.company,
            duration=request.duration,
            db=db
        )
        
        if not questions:
            raise HTTPException(
                status_code=404, 
                detail=f"No questions found for {request.interview_type} at {request.difficulty} level"
            )
        
        # Create session in database
        session = InterviewSession(
            session_id=session_id,
            interview_type=request.interview_type,
            difficulty_level=request.difficulty,
            company=request.company,
            duration_minutes=request.duration,
            status='in_progress'
        )
        db.add(session)
        db.commit()
        
        # Configure VAPI assistant
        question_texts = [q['question_text'] for q in questions]
        vapi_config = vapi_manager.create_assistant_config(
            session_id=session_id,
            interview_type=request.interview_type,
            questions=question_texts
        )
        
        # Create VAPI assistant
        assistant_result = vapi_manager.create_assistant(vapi_config)
        assistant_id = assistant_result.get('id') if 'error' not in assistant_result else None
        
        return InterviewStartResponse(
            session_id=session_id,
            questions=questions,
            vapi_config=vapi_config,
            assistant_id=assistant_id
        )
        
    except Exception as e:
        logger.error(f"Error starting interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/analyze-response", response_model=ResponseAnalysisResult)
async def analyze_response(request: ResponseAnalysisRequest, db: Session = Depends(get_db)):
    """
    Analyze a single interview response using ML model
    """
    try:
        # Get question details
        question = db.query(InterviewQuestion).filter(
            InterviewQuestion.question_id == request.question_id
        ).first()
        
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Get session details
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Analyze response using ML model
        analysis = analyzer.analyze_response(
            response_text=request.response_text,
            question_text=question.question_text,
            interview_type=session.interview_type
        )
        
        # Store response in database
        response_record = SessionResponse(
            session_id=request.session_id,
            question_id=request.question_id,
            question_number=request.question_number,
            response_text=request.response_text,
            word_count=analysis['features'].get('word_count', 0),
            filler_word_count=analysis['features'].get('filler_word_count', 0),
            technical_term_count=analysis['features'].get('technical_term_count', 0),
            average_word_length=analysis['features'].get('avg_word_length', 0),
            content_quality_score=analysis['scores']['content_quality'],
            communication_score=analysis['scores']['communication'],
            confidence_score=analysis['scores']['confidence'],
            technical_accuracy_score=analysis['scores']['technical_accuracy'],
            overall_response_score=analysis['overall_score'],
            response_rating=analysis['rating']
        )
        db.add(response_record)
        db.commit()
        db.refresh(response_record)
        
        # Generate and store feedback
        feedback_suggestions = analyzer.generate_feedback_suggestions(analysis)
        for feedback_item in feedback_suggestions:
            feedback = FeedbackDetail(
                session_id=request.session_id,
                response_id=response_record.response_id,
                feedback_type=feedback_item['type'],
                feedback_text=feedback_item['message']
            )
            db.add(feedback)
        db.commit()
        
        return ResponseAnalysisResult(
            response_id=response_record.response_id,
            quality_score=analysis['overall_score'],
            content_quality=analysis['scores']['content_quality'],
            communication=analysis['scores']['communication'],
            confidence=analysis['scores']['confidence'],
            technical_accuracy=analysis['scores']['technical_accuracy'],
            rating=analysis['rating'],
            feedback=feedback_suggestions,
            metrics=analysis['features']
        )
        
    except Exception as e:
        logger.error(f"Error analyzing response: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/interview/end", response_model=FeedbackResponse)
async def end_interview(request: EndInterviewRequest, db: Session = Depends(get_db)):
    """
    End interview session and generate comprehensive feedback
    """
    try:
        # Get session
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get all responses for this session
        responses = db.query(SessionResponse).filter(
            SessionResponse.session_id == request.session_id
        ).order_by(SessionResponse.question_number).all()
        
        if not responses:
            raise HTTPException(status_code=400, detail="No responses found for this session")
        
        # Calculate overall metrics
        overall_analysis = calculate_overall_feedback(responses, db)
        
        # Update session
        session.status = 'completed'
        session.completed_at = datetime.utcnow()
        session.overall_score = overall_analysis['overall_score']
        session.overall_rating = overall_analysis['overall_rating']
        db.commit()
        
        # Generate detailed breakdown
        question_breakdown = []
        for response in responses:
            # Get question details
            question = db.query(InterviewQuestion).filter(
                InterviewQuestion.question_id == response.question_id
            ).first()
            
            # Get feedback for this response
            feedback_items = db.query(FeedbackDetail).filter(
                FeedbackDetail.response_id == response.response_id
            ).all()
            
            question_breakdown.append({
                'question_number': response.question_number,
                'question_text': question.question_text if question else "Question not found",
                'response_text': response.response_text,
                'scores': {
                    'content_quality': float(response.content_quality_score or 0),
                    'communication': float(response.communication_score or 0),
                    'confidence': float(response.confidence_score or 0),
                    'technical_accuracy': float(response.technical_accuracy_score or 0),
                    'overall': float(response.overall_response_score or 0)
                },
                'rating': response.response_rating,
                'feedback': [{'type': f.feedback_type, 'message': f.feedback_text} for f in feedback_items]
            })
        
        return FeedbackResponse(
            session_id=request.session_id,
            overall_score=overall_analysis['overall_score'],
            overall_rating=overall_analysis['overall_rating'],
            strengths=overall_analysis['strengths'],
            improvements=overall_analysis['improvements'],
            detailed_analysis=overall_analysis['detailed_metrics'],
            question_breakdown=question_breakdown
        )
        
    except Exception as e:
        logger.error(f"Error ending interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Question Management Endpoints
@app.get("/api/questions/{interview_type}", response_model=QuestionResponse)
async def get_questions(
    interview_type: str, 
    difficulty: Optional[str] = None, 
    company: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get available questions for a specific interview type
    """
    try:
        query = db.query(InterviewQuestion).filter(
            InterviewQuestion.interview_type == interview_type
        )
        
        if difficulty:
            query = query.filter(InterviewQuestion.difficulty_level == difficulty)
        
        if company:
            query = query.filter(InterviewQuestion.company == company)
        
        questions = query.all()
        
        question_list = [
            {
                'question_id': q.question_id,
                'question_text': q.question_text,
                'difficulty': q.difficulty_level,
                'category': q.category,
                'company': q.company,
                'expected_keywords': q.expected_keywords
            }
            for q in questions
        ]
        
        return QuestionResponse(
            questions=question_list,
            count=len(question_list)
        )
        
    except Exception as e:
        logger.error(f"Error getting questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Session Management Endpoints
@app.get("/api/session/{session_id}")
async def get_session_details(session_id: str, db: Session = Depends(get_db)):
    """
    Get details of a specific interview session
    """
    try:
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        responses = db.query(SessionResponse).filter(
            SessionResponse.session_id == session_id
        ).all()
        
        return {
            "session_id": session.session_id,
            "interview_type": session.interview_type,
            "difficulty_level": session.difficulty_level,
            "company": session.company,
            "duration_minutes": session.duration_minutes,
            "status": session.status,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "overall_score": float(session.overall_score) if session.overall_score else None,
            "overall_rating": session.overall_rating,
            "responses_count": len(responses)
        }
        
    except Exception as e:
        logger.error(f"Error getting session details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# VAPI Webhook Endpoints
@app.post("/api/vapi/webhook")
async def handle_vapi_webhook(request: Request):
    """
    Handle VAPI webhook events
    """
    try:
        # Get raw payload for signature validation
        payload = await request.body()
        signature = request.headers.get('x-vapi-signature', '')
        
        # Validate webhook signature
        if not vapi_manager.validate_webhook_signature(payload.decode(), signature):
            raise HTTPException(status_code=401, detail="Invalid webhook signature")
        
        # Parse JSON payload
        webhook_data = await request.json()
        
        # Handle the webhook
        result = vapi_manager.handle_webhook(webhook_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error handling VAPI webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility Functions
def get_questions_for_interview(
    interview_type: str, 
    difficulty: str, 
    company: Optional[str], 
    duration: int, 
    db: Session
) -> List[Dict[str, Any]]:
    """
    Retrieve appropriate questions based on interview parameters
    """
    # Calculate number of questions based on duration
    # Assume 8-10 minutes per question for technical, 6-8 for behavioral
    minutes_per_question = 9 if interview_type.startswith('technical') else 7
    num_questions = max(3, min(10, duration // minutes_per_question))
    
    # Query questions
    query = db.query(InterviewQuestion).filter(
        InterviewQuestion.interview_type == interview_type,
        InterviewQuestion.difficulty_level == difficulty
    )
    
    # Add company filter if specified
    if company:
        company_questions = query.filter(InterviewQuestion.company == company).limit(num_questions).all()
        if len(company_questions) < num_questions:
            # Fill remaining with generic questions
            generic_questions = query.filter(InterviewQuestion.company.is_(None)).limit(
                num_questions - len(company_questions)
            ).all()
            all_questions = company_questions + generic_questions
        else:
            all_questions = company_questions
    else:
        all_questions = query.limit(num_questions).all()
    
    return [
        {
            "question_id": q.question_id,
            "question_text": q.question_text,
            "category": q.category,
            "expected_keywords": q.expected_keywords,
            "difficulty": q.difficulty_level,
            "company": q.company
        }
        for q in all_questions
    ]

def calculate_overall_feedback(responses: List[SessionResponse], db: Session) -> Dict[str, Any]:
    """
    Calculate comprehensive feedback across all responses
    """
    if not responses:
        return {
            "overall_score": 0.0,
            "overall_rating": "insufficient_data",
            "strengths": [],
            "improvements": ["Complete more questions to get detailed feedback"],
            "detailed_metrics": {}
        }
    
    # Calculate averages
    avg_content = sum(float(r.content_quality_score or 0) for r in responses) / len(responses)
    avg_communication = sum(float(r.communication_score or 0) for r in responses) / len(responses)
    avg_confidence = sum(float(r.confidence_score or 0) for r in responses) / len(responses)
    avg_technical = sum(float(r.technical_accuracy_score or 0) for r in responses) / len(responses)
    
    overall_score = (avg_content + avg_communication + avg_confidence + avg_technical) / 4
    
    # Determine overall rating
    if overall_score >= 8.5:
        overall_rating = "excellent"
    elif overall_score >= 7.0:
        overall_rating = "good"
    elif overall_score >= 5.0:
        overall_rating = "average"
    else:
        overall_rating = "needs_improvement"
    
    # Aggregate metrics
    total_words = sum(r.word_count or 0 for r in responses)
    total_filler_words = sum(r.filler_word_count or 0 for r in responses)
    total_tech_terms = sum(r.technical_term_count or 0 for r in responses)
    avg_word_length = sum(float(r.average_word_length or 0) for r in responses) / len(responses)
    
    # Identify strengths and improvements
    strengths = []
    improvements = []
    
    if avg_communication >= 8.0:
        strengths.append("Excellent communication skills with clear articulation")
    if avg_technical >= 8.0:
        strengths.append("Strong technical knowledge and accurate explanations")
    if avg_confidence >= 8.0:
        strengths.append("Confident and assertive delivery throughout")
    if total_filler_words / len(responses) <= 2:
        strengths.append("Professional speech with minimal filler words")
    if avg_content >= 8.0:
        strengths.append("Well-structured responses with good depth and examples")
    
    if avg_communication < 6.0:
        improvements.append("Work on clarity and structure of responses")
    if avg_technical < 6.0:
        improvements.append("Deepen technical knowledge in key areas")
    if avg_confidence < 6.0:
        improvements.append("Practice to build confidence in your delivery")
    if total_filler_words / len(responses) > 5:
        improvements.append("Reduce filler words through practice and pausing")
    if avg_content < 6.0:
        improvements.append("Provide more detailed answers with specific examples")
    
    # If no specific improvements identified, add general advice
    if not improvements:
        improvements.append("Continue practicing to maintain your strong performance")
    
    detailed_metrics = {
        "average_scores": {
            "content_quality": round(avg_content, 2),
            "communication": round(avg_communication, 2),
            "confidence": round(avg_confidence, 2),
            "technical_accuracy": round(avg_technical, 2)
        },
        "aggregated_stats": {
            "total_words": total_words,
            "total_filler_words": total_filler_words,
            "total_tech_terms": total_tech_terms,
            "responses_count": len(responses),
            "avg_word_length": round(avg_word_length, 2),
            "filler_word_ratio": round((total_filler_words / total_words) if total_words > 0 else 0, 4)
        }
    }
    
    return {
        "overall_score": round(overall_score, 2),
        "overall_rating": overall_rating,
        "strengths": strengths,
        "improvements": improvements,
        "detailed_metrics": detailed_metrics
    }

# Resume Analysis Endpoints
class ResumeAnalysisResponse(BaseModel):
    overall_score: int
    ats_score: int
    rating: str
    category_scores: Dict[str, int]
    key_strengths: List[str]
    critical_issues: List[Dict[str, str]]
    missing_sections: List[str]
    keyword_analysis: Dict[str, Any]
    formatting_issues: List[str]
    recommendations: List[str]
    summary: str

@app.post("/api/resume/analyze", response_model=ResumeAnalysisResponse)
async def analyze_resume(
    file: UploadFile = File(..., description="Resume file (PDF, DOCX, or TXT)"),
    job_description: Optional[str] = Form(None),
    target_role: Optional[str] = Form(None)
):
    """
    Analyze a resume file for ATS compatibility and provide actionable feedback.
    Accepts PDF, DOCX, or TXT file formats.
    """
    try:
        # Validate file extension
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        allowed_extensions = ['.pdf', '.docx', '.txt']
        file_ext = '.' + file.filename.lower().split('.')[-1]
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file format. Please upload PDF, DOCX, or TXT files."
            )
        
        # Read file content
        file_content = await file.read()
        
        # Extract text from file
        try:
            resume_text = FileParser.extract_text(file_content, file.filename)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        
        if not resume_text or len(resume_text.strip()) < 50:
            raise HTTPException(
                status_code=400,
                detail="Unable to extract sufficient text from the file. Please ensure the file is not empty or corrupted."
            )
        
        # Analyze the resume using the LLM service
        analysis = resume_analyzer.analyze_resume(
            resume_text=resume_text,
            job_description=job_description or '',
            target_role=target_role or ''
        )
        
        return ResumeAnalysisResponse(**analysis)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        raise HTTPException(status_code=500, detail=f"Resume analysis failed: {str(e)}")


# R
# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )