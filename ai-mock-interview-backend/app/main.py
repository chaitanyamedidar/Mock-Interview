from fastapi import FastAPI, HTTPException, Depends, status, Request, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse
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
from .models import InterviewSession, SessionResponse, InterviewQuestion, InterviewReport
from .vapi_service import VAPIManager
from .vapi_interview_service import VAPIInterviewAnalyzer
from .resume_service import ATSResumeAnalyzer
from .file_parser import FileParser
from .question_service import get_question_service

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
vapi_manager = VAPIManager()
interview_analyzer = VAPIInterviewAnalyzer()
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

class TranscriptMessage(BaseModel):
    role: str
    message: str
    timestamp: Optional[str] = None

class EndInterviewRequest(BaseModel):
    session_id: str
    transcript: Optional[List[TranscriptMessage]] = None

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



@app.post("/api/interview/end", response_model=FeedbackResponse)
async def end_interview(request: EndInterviewRequest, db: Session = Depends(get_db)):
    """
    End interview session and generate comprehensive feedback.
    Supports both VAPI webhook-based reports and direct transcript submission.
    """
    try:
        # Get session
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == request.session_id
        ).first()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # 1. If transcript is provided directly (Frontend fallback), process it immediately
        if request.transcript:
            logger.info(f"Processing provided transcript for session {request.session_id}")
            
            # Construct mock VAPI payload
            mock_payload = {
                "call": {
                    "id": "manual_submission_" + request.session_id,
                    "duration": 0, # We might not have duration
                    "metadata": {
                        "session_id": request.session_id,
                        "interview_type": session.interview_type,
                        "user_id": session.user_id
                    },
                    "transcript": {
                        "messages": [
                            {
                                "role": msg.role,
                                "message": msg.message,
                                "timestamp": msg.timestamp or datetime.utcnow().isoformat()
                            }
                            for msg in request.transcript
                        ]
                    }
                }
            }
            
            # Process using VAPI analyzer
            try:
                analysis_result = await interview_analyzer.process_interview_transcript(mock_payload, db)
                logger.info(f"Analysis completed for session {request.session_id}")
                
                # The report is already saved by process_interview_transcript
                # Now fetch it fresh and return
                report = db.query(InterviewReport).filter(
                    InterviewReport.session_id == request.session_id
                ).first()
                
                if report:
                    # Update session status
                    session.status = 'completed'
                    session.completed_at = datetime.utcnow()
                    session.overall_score = report.overall_score
                    session.overall_rating = report.performance_label
                    db.commit()
                    
                    return FeedbackResponse(
                        session_id=request.session_id,
                        overall_score=float(report.overall_score),
                        overall_rating=report.performance_label,
                        strengths=[r['description'] for r in report.recommendations if 'Strength' in r.get('title', '')] or ["Good interview performance"],
                        improvements=[r['description'] for r in report.recommendations if 'Strength' not in r.get('title', '')],
                        detailed_analysis=report.category_scores,
                        question_breakdown=report.transcript if report.transcript else []
                    )
                
            except Exception as e:
                logger.error(f"Error processing manual transcript: {e}", exc_info=True)
                # Fallthrough to try fetching existing report/responses
        
        # 2. Check for existing InterviewReport (from VAPI webhook or just created above)
        report = db.query(InterviewReport).filter(
            InterviewReport.session_id == request.session_id
        ).first()
        
        if report:
             # Map InterviewReport to FeedbackResponse
             # Note: InterviewReport stores `category_scores` as JSON, `recommendations` as JSON
             
             return FeedbackResponse(
                session_id=request.session_id,
                overall_score=float(report.overall_score),
                overall_rating=report.performance_label,
                strengths=[r['description'] for r in report.recommendations if 'Strength' in r.get('title', '')] or ["Check detailed report"], # Simple extraction
                improvements=[r['description'] for r in report.recommendations if 'Strength' not in r.get('title', '')],
                detailed_analysis=report.category_scores, # This was detailed_metrics
                question_breakdown=report.transcript if report.transcript else [] # Enriched transcript
             )

        # 3. Fallback: Old SessionResponse logic (Non-VAPI)
        # Get all responses for this session
        responses = db.query(SessionResponse).filter(
            SessionResponse.session_id == request.session_id
        ).order_by(SessionResponse.question_number).all()
        
        if not responses:
            raise HTTPException(status_code=400, detail="No responses or report found for this session")
        
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
                'rating': response.response_rating
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

# Background analysis task wrapper
async def run_analysis_background(webhook_data: Dict[str, Any]):
    """Run interview analysis in background with fresh DB session"""
    db = SessionLocal()
    try:
        logger.info(f"Starting background analysis for call {webhook_data.get('call', {}).get('id')}")
        await interview_analyzer.process_interview_transcript(webhook_data, db)
        logger.info("Background analysis completed successfully")
    except Exception as e:
        logger.error(f"Background analysis failed: {e}")
    finally:
        db.close()

# VAPI Webhook Endpoints
@app.post("/api/vapi/webhook")

@app.post("/api/vapi/webhook")
async def handle_vapi_webhook(request: Request, background_tasks: BackgroundTasks):
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
        
        # Check if analysis should be triggered
        if result.get('status') == 'call_ended':
            # Run analysis in background
            background_tasks.add_task(run_analysis_background, webhook_data)
            logger.info("Queued background analysis for call")
        
        return result
        
    except Exception as e:
        logger.error(f"Error handling VAPI webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/vapi/interview-complete")
async def handle_interview_complete(request: Request, db: Session = Depends(get_db)):
    """
    Handle VAPI interview completion webhook.
    Receives transcript, analyzes with hybrid rule-based + LLM approach,
    returns structured feedback matching frontend schema.
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
        
        # Handle implicit 'message' wrapper from VAPI
        if 'message' in webhook_data:
            webhook_data = webhook_data['message']

        # Log the message type for debugging
        message_type = webhook_data.get('type')
        logger.info(f"Received VAPI webhook event type: {message_type}")

        # If this is not an end-of-call-report or doesn't have a transcript, we might want to ignore it 
        # to prevent 400 errors on call setup/status events (call-start, etc.)
        if message_type in ['call-start', 'status-update', 'speech-update', 'function-call']:
            return {"status": "ignored", "reason": f"Event {message_type} handled elsewhere or ignored"}

        # Validate payload structure
        call_data = webhook_data.get('call', {})
        if not call_data:
            logger.error("Missing 'call' data in payload")
            raise HTTPException(status_code=400, detail="Missing 'call' data in payload")
        
        transcript_data = call_data.get('transcript', {})
        messages = transcript_data.get('messages', [])
        
        if not messages:
            logger.error("No transcript data found in payload")
            raise HTTPException(status_code=400, detail="No transcript data found")
        
        metadata = call_data.get('metadata', {})
        session_id = metadata.get('session_id')
        
        if not session_id:
            logger.error("Missing session_id in metadata")
            raise HTTPException(status_code=400, detail="Missing session_id in metadata")
        
        # Process interview transcript
        logger.info(f"Processing interview completion for session {session_id}")
        
        try:
            analysis_result = await interview_analyzer.process_interview_transcript(
                vapi_payload=webhook_data,
                db=db
            )
            
            logger.info(f"Successfully analyzed interview for session {session_id}")
            return analysis_result
        
        except ValueError as e:
            # Validation errors (e.g., no questions found)
            logger.error(f"Validation error processing interview: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        
        except Exception as e:
            # Unexpected errors during processing
            logger.error(f"Error processing interview transcript: {e}")
            raise HTTPException(
                status_code=500, 
                detail="Failed to process interview. Please try again."
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error handling interview complete webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/interview/results/{session_id}")
async def get_interview_results(session_id: str, db: Session = Depends(get_db)):
    """
    Poll for interview results by session_id.
    Returns 202 if still processing, 200 with data if ready, 404 if not found.
    """
    try:
        # Query for the interview report
        report = db.query(InterviewReport).filter(
            InterviewReport.session_id == session_id
        ).first()
        
        if not report:
            raise HTTPException(
                status_code=404,
                detail=f"Interview session '{session_id}' not found"
            )
        
        # Check if analysis is complete
        if not report.category_scores or not report.recommendations:
            # Still processing
            return JSONResponse(
                status_code=202,
                content={
                    "message": "Analysis in progress",
                    "session_id": session_id,
                    "status": "processing"
                }
            )
        
        # Results ready - return complete analysis
        return {
            "report_summary": {
                "overall_score": float(report.overall_score),
                "performance_label": report.performance_label,
                "total_questions_analyzed": report.total_questions_analyzed,
                "categories": report.category_scores
            },
            "ai_recommendations": report.recommendations,
            "questions_breakdown": report.transcript, # This now contains the analyzed Q&A
            "metadata": {
                "session_id": report.session_id,
                "analysis_timestamp": report.created_at.isoformat() if report.created_at else None,
                "call_duration": report.call_duration_seconds
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching interview results: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch results")


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
        analysis = await resume_analyzer.analyze_resume(
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


# ============================================================================
# CODING QUESTION ENDPOINTS
# ============================================================================

@app.get("/api/v1/questions/stats")
async def get_question_stats():
    """Get statistics about the question database."""
    try:
        service = get_question_service()
        return service.get_statistics()
    except Exception as e:
        logger.error(f"Error getting question stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/questions/random")
async def get_random_question(
    company: Optional[str] = None,
    difficulty: Optional[str] = None,
    topic: Optional[str] = None
):
    """
    Get a random question matching the specified filters.
    
    Query Parameters:
        company: Filter by company (e.g., "JP Morgan", "Capgemini", "Deloitte")
        difficulty: Filter by difficulty ("Easy", "Medium", "Hard")
        topic: Filter by topic (e.g., "Array", "Hash Table", "Dynamic Programming")
    """
    try:
        service = get_question_service()
        question = service.get_random_question(company=company, difficulty=difficulty, topic=topic)
        
        if not question:
            raise HTTPException(
                status_code=404,
                detail=f"No questions found matching filters: company={company}, difficulty={difficulty}, topic={topic}"
            )
        
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting random question: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/questions/{question_id}")
async def get_question_by_id(question_id: str):
    """Get a specific question by its ID."""
    try:
        service = get_question_service()
        question = service.get_question_by_id(question_id)
        
        if not question:
            raise HTTPException(status_code=404, detail=f"Question not found: {question_id}")
        
        return question
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question by ID: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/questions/company/{company}")
async def get_questions_by_company(company: str):
    """Get all questions for a specific company."""
    try:
        service = get_question_service()
        questions = service.get_questions_by_company(company)
        
        return {
            "company": company,
            "count": len(questions),
            "questions": questions
        }
    except Exception as e:
        logger.error(f"Error getting questions by company: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/questions/difficulty/{difficulty}")
async def get_questions_by_difficulty(difficulty: str):
    """Get all questions of a specific difficulty level."""
    try:
        service = get_question_service()
        questions = service.get_questions_by_difficulty(difficulty)
        
        return {
            "difficulty": difficulty,
            "count": len(questions),
            "questions": questions
        }
    except Exception as e:
        logger.error(f"Error getting questions by difficulty: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/questions/topic/{topic}")
async def get_questions_by_topic(topic: str):
    """Get all questions for a specific topic."""
    try:
        service = get_question_service()
        questions = service.get_questions_by_topic(topic)
        
        return {
            "topic": topic,
            "count": len(questions),
            "questions": questions
        }
    except Exception as e:
        logger.error(f"Error getting questions by topic: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/questions/search")
async def search_questions(q: str, limit: int = 10):
    """
    Search questions by title or description.
    
    Query Parameters:
        q: Search query string
        limit: Maximum number of results (default: 10)
    """
    try:
        service = get_question_service()
        questions = service.search_questions(query=q, limit=limit)
        
        return {
            "query": q,
            "count": len(questions),
            "questions": questions
        }
    except Exception as e:
        logger.error(f"Error searching questions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )