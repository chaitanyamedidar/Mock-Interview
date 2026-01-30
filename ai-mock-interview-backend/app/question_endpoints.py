"""
API endpoints for the coding question system.
Add these endpoints to your main.py file.
"""

# ============================================================================
# CODING QUESTION ENDPOINTS
# ============================================================================

from fastapi import HTTPException
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Import at the top of main.py:
# from .question_service import get_question_service

# Add these endpoints to your FastAPI app:

"""
@app.get("/api/v1/questions/stats")
async def get_question_stats():
    '''Get statistics about the question database.'''
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
    '''
    Get a random question matching the specified filters.
    
    Query Parameters:
        company: Filter by company (e.g., "JP Morgan", "Capgemini", "Deloitte")
        difficulty: Filter by difficulty ("Easy", "Medium", "Hard")
        topic: Filter by topic (e.g., "Array", "Hash Table", "Dynamic Programming")
    '''
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
    '''Get a specific question by its ID.'''
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
    '''Get all questions for a specific company.'''
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
    '''Get all questions of a specific difficulty level.'''
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
    '''Get all questions for a specific topic.'''
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
    '''
    Search questions by title or description.
    
    Query Parameters:
        q: Search query string
        limit: Maximum number of results (default: 10)
    '''
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
"""
