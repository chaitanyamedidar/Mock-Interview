"""
Question Service for loading and serving original coding questions.
Provides in-memory caching for fast API responses.
"""

import json
import os
import random
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class QuestionService:
    """Service for managing and retrieving coding questions."""
    
    def __init__(self):
        """Initialize the question service and load questions into memory."""
        self.questions = []
        self.questions_by_id = {}
        self.questions_by_company = {}
        self.questions_by_difficulty = {}
        self.questions_by_topic = {}
        self.patterns = {}
        self._load_data()
    
    def _load_data(self):
        """Load questions and patterns from JSON files."""
        try:
            # Get data directory path
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)
            data_dir = os.path.join(project_root, "data")
            
            # Load questions
            questions_file = os.path.join(data_dir, "original_questions.json")
            with open(questions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.questions = data.get("questions", [])
            
            # Load patterns
            patterns_file = os.path.join(data_dir, "pattern_library.json")
            with open(patterns_file, 'r', encoding='utf-8') as f:
                self.patterns = json.load(f)
            
            # Build indexes for fast lookup
            self._build_indexes()
            
            logger.info(f"Loaded {len(self.questions)} questions successfully")
            
        except Exception as e:
            logger.error(f"Error loading question data: {e}")
            raise
    
    def _build_indexes(self):
        """Build indexes for efficient question retrieval."""
        for question in self.questions:
            # Index by ID
            self.questions_by_id[question["id"]] = question
            
            # Index by company
            for company in question.get("companies", []):
                if company not in self.questions_by_company:
                    self.questions_by_company[company] = []
                self.questions_by_company[company].append(question)
            
            # Index by difficulty
            difficulty = question.get("difficulty", "Medium")
            if difficulty not in self.questions_by_difficulty:
                self.questions_by_difficulty[difficulty] = []
            self.questions_by_difficulty[difficulty].append(question)
            
            # Index by topic
            for topic in question.get("topics", []):
                if topic not in self.questions_by_topic:
                    self.questions_by_topic[topic] = []
                self.questions_by_topic[topic].append(question)
    
    def get_question_by_id(self, question_id: str) -> Optional[Dict]:
        """
        Get a specific question by ID.
        
        Args:
            question_id: Unique question identifier
        
        Returns:
            Question dictionary or None if not found
        """
        return self.questions_by_id.get(question_id)
    
    def get_random_question(
        self, 
        company: Optional[str] = None,
        difficulty: Optional[str] = None,
        topic: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Get a random question matching the specified filters.
        
        Args:
            company: Filter by company (e.g., "JP Morgan")
            difficulty: Filter by difficulty ("Easy", "Medium", "Hard")
            topic: Filter by topic (e.g., "Array", "Hash Table")
        
        Returns:
            Random question matching filters or None if no matches
        """
        # Start with all questions
        candidates = self.questions.copy()
        
        # Apply filters
        if company:
            candidates = [q for q in candidates if company in q.get("companies", [])]
        
        if difficulty:
            candidates = [q for q in candidates if q.get("difficulty") == difficulty]
        
        if topic:
            candidates = [q for q in candidates if topic in q.get("topics", [])]
        
        # Return random question from candidates
        if candidates:
            return random.choice(candidates)
        return None
    
    def get_questions_by_company(self, company: str) -> List[Dict]:
        """
        Get all questions for a specific company.
        
        Args:
            company: Company name
        
        Returns:
            List of questions for the company
        """
        return self.questions_by_company.get(company, [])
    
    def get_questions_by_difficulty(self, difficulty: str) -> List[Dict]:
        """
        Get all questions of a specific difficulty.
        
        Args:
            difficulty: Difficulty level ("Easy", "Medium", "Hard")
        
        Returns:
            List of questions at that difficulty
        """
        return self.questions_by_difficulty.get(difficulty, [])
    
    def get_questions_by_topic(self, topic: str) -> List[Dict]:
        """
        Get all questions for a specific topic.
        
        Args:
            topic: Topic name (e.g., "Array", "Dynamic Programming")
        
        Returns:
            List of questions covering that topic
        """
        return self.questions_by_topic.get(topic, [])
    
    def get_statistics(self) -> Dict:
        """
        Get statistics about the question database.
        
        Returns:
            Dictionary with question statistics
        """
        return {
            "total_questions": len(self.questions),
            "by_difficulty": {
                difficulty: len(questions)
                for difficulty, questions in self.questions_by_difficulty.items()
            },
            "by_company": {
                company: len(questions)
                for company, questions in self.questions_by_company.items()
            },
            "by_topic": {
                topic: len(questions)
                for topic, questions in self.questions_by_topic.items()
            },
            "total_patterns": len(self.patterns),
            "companies": list(self.questions_by_company.keys()),
            "difficulties": list(self.questions_by_difficulty.keys()),
            "topics": list(self.questions_by_topic.keys())
        }
    
    def search_questions(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search questions by title or description.
        
        Args:
            query: Search query string
            limit: Maximum number of results
        
        Returns:
            List of matching questions
        """
        query_lower = query.lower()
        results = []
        
        for question in self.questions:
            title = question.get("title", "").lower()
            description = question.get("description", "").lower()
            
            if query_lower in title or query_lower in description:
                results.append(question)
                
                if len(results) >= limit:
                    break
        
        return results

# Global instance
_question_service = None

def get_question_service() -> QuestionService:
    """Get or create the global question service instance."""
    global _question_service
    if _question_service is None:
        _question_service = QuestionService()
    return _question_service
