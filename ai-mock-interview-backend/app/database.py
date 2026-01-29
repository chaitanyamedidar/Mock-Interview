from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import json
from dotenv import load_dotenv
from .models import InterviewQuestion

load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./interview_platform.db')

# Create engine
engine = create_engine(
    DATABASE_URL,
    echo=True if os.getenv('DEBUG') == 'True' else False
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base for models
Base = declarative_base()

def get_db():
    """
    Dependency for FastAPI to get database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    Initialize database and create tables
    """
    from .models import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

def seed_questions():
    """
    Seed database with interview questions from JSON file
    """
    from .models import InterviewQuestion
    
    db = SessionLocal()
    
    # Check if questions already exist
    existing_questions = db.query(InterviewQuestion).first()
    if existing_questions:
        print("Questions already seeded")
        db.close()
        return
    
    # Load questions from JSON file
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'interview-questions.json')
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Warning: {json_path} not found. Skipping question seeding.")
        db.close()
        return
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON file: {e}")
        db.close()
        return
    
    all_questions = []
    
    # Parse Technical Questions
    if 'technical_questions' in data:
        tech_data = data['technical_questions']
        
        # Computer Science questions
        if 'computer_science' in tech_data:
            cs_data = tech_data['computer_science']
            for subcategory, questions in cs_data.items():
                for q in questions:
                    all_questions.append({
                        'question_text': q['question'],
                        'interview_type': 'technical_software',
                        'difficulty_level': q['difficulty'],
                        'category': subcategory,
                        'expected_keywords': q.get('topics', [])
                    })
        
        # Programming Languages questions
        if 'programming_languages' in tech_data:
            for lang, questions in tech_data['programming_languages'].items():
                for q in questions:
                    all_questions.append({
                        'question_text': q['question'],
                        'interview_type': 'technical_software',
                        'difficulty_level': q['difficulty'],
                        'category': lang,
                        'expected_keywords': q.get('topics', [])
                    })
        
        # System Design questions
        if 'system_design' in tech_data:
            for q in tech_data['system_design']:
                all_questions.append({
                    'question_text': q['question'],
                    'interview_type': 'technical_software',
                    'difficulty_level': q['difficulty'],
                    'category': 'system_design',
                    'expected_keywords': q.get('topics', [])
                })
    
    # Parse Behavioral Questions
    if 'behavioral_questions' in data:
        beh_data = data['behavioral_questions']
        for category, questions in beh_data.items():
            for q in questions:
                all_questions.append({
                    'question_text': q['question'],
                    'interview_type': 'behavioral',
                    'difficulty_level': q.get('difficulty', 'medium'),
                    'category': category,
                    'expected_keywords': q.get('tips', [])
                })
    
    # Parse Coding Challenges
    if 'coding_challenges' in data:
        coding_data = data['coding_challenges']
        for difficulty_level, questions in coding_data.items():
            for q in questions:
                all_questions.append({
                    'question_text': q['question'],
                    'interview_type': 'coding',
                    'difficulty_level': difficulty_level,
                    'category': 'coding_challenge',
                    'expected_keywords': q.get('topics', [])
                })
    
    # Fallback: if JSON parsing failed, use some basic hardcoded questions
    if not all_questions:
        print("Warning: No questions loaded from JSON. Using fallback questions.")
        all_questions = [
            {
                'question_text': 'Explain the difference between REST and GraphQL APIs',
                'interview_type': 'technical_software',
                'difficulty_level': 'medium',
                'category': 'web_development',
                'expected_keywords': ['REST', 'GraphQL', 'HTTP', 'query', 'endpoint']
            },
            {
                'question_text': 'Tell me about a time you faced a difficult technical challenge',
                'interview_type': 'behavioral',
                'difficulty_level': 'medium',
                'category': 'problem_solving',
                'expected_keywords': ['challenge', 'approach', 'solution', 'result']
            }
        ]
    
    # Add to database
    for q_data in all_questions:
        question = InterviewQuestion(**q_data)
        db.add(question)
    
    db.commit()
    db.close()
    print(f"✅ Successfully seeded {len(all_questions)} questions from JSON file")

if __name__ == '__main__':
    init_database()
    seed_questions()
