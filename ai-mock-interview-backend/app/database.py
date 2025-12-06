from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
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
    Seed database with sample interview questions
    """
    from .models import InterviewQuestion
    
    db = SessionLocal()
    
    # Check if questions already exist
    existing_questions = db.query(InterviewQuestion).first()
    if existing_questions:
        print("Questions already seeded")
        db.close()
        return
    
    # Technical Software Engineering Questions
    technical_questions = [
        {
            'question_text': 'Explain the difference between REST and GraphQL APIs',
            'interview_type': 'technical_software',
            'difficulty_level': 'medium',
            'category': 'web_development',
            'expected_keywords': ['REST', 'GraphQL', 'HTTP', 'query', 'endpoint']
        },
        {
            'question_text': 'What is the time complexity of binary search and explain how it works?',
            'interview_type': 'technical_software',
            'difficulty_level': 'medium',
            'category': 'algorithms',
            'expected_keywords': ['O(log n)', 'divide', 'conquer', 'sorted', 'array']
        },
        {
            'question_text': 'Describe how you would design a URL shortener like bit.ly',
            'interview_type': 'technical_software',
            'difficulty_level': 'hard',
            'category': 'system_design',
            'expected_keywords': ['hashing', 'database', 'scalability', 'redirect', 'unique']
        },
        {
            'question_text': 'Explain the concept of database indexing and when you would use it',
            'interview_type': 'technical_software',
            'difficulty_level': 'medium',
            'category': 'databases',
            'expected_keywords': ['B-tree', 'performance', 'query', 'primary key', 'foreign key']
        },
        {
            'question_text': 'What are the SOLID principles in object-oriented programming?',
            'interview_type': 'technical_software',
            'difficulty_level': 'medium',
            'category': 'programming_concepts',
            'expected_keywords': ['single responsibility', 'open-closed', 'liskov', 'interface', 'dependency']
        },
        {
            'question_text': 'Explain the difference between var, let, and const in JavaScript',
            'interview_type': 'technical_software',
            'difficulty_level': 'easy',
            'category': 'javascript',
            'expected_keywords': ['scope', 'hoisting', 'block scope', 'immutable', 'redeclaration']
        },
        {
            'question_text': 'What is a closure in JavaScript and provide an example?',
            'interview_type': 'technical_software',
            'difficulty_level': 'medium',
            'category': 'javascript',
            'expected_keywords': ['closure', 'lexical scope', 'function', 'encapsulation', 'private variables']
        },
        {
            'question_text': 'Explain the concept of microservices architecture',
            'interview_type': 'technical_software',
            'difficulty_level': 'hard',
            'category': 'system_design',
            'expected_keywords': ['microservices', 'monolith', 'distributed', 'independence', 'communication']
        },
        {
            'question_text': 'What is the difference between SQL and NoSQL databases?',
            'interview_type': 'technical_software',
            'difficulty_level': 'easy',
            'category': 'databases',
            'expected_keywords': ['SQL', 'NoSQL', 'relational', 'document', 'scalability']
        },
        {
            'question_text': 'Implement a function to reverse a linked list',
            'interview_type': 'technical_software',
            'difficulty_level': 'medium',
            'category': 'data_structures',
            'expected_keywords': ['linked list', 'pointer', 'iteration', 'recursion', 'reverse']
        }
    ]
    
    # Behavioral Questions
    behavioral_questions = [
        {
            'question_text': 'Tell me about a time you faced a difficult technical challenge and how you overcame it',
            'interview_type': 'behavioral',
            'difficulty_level': 'medium',
            'category': 'problem_solving',
            'expected_keywords': ['challenge', 'approach', 'solution', 'result', 'learned']
        },
        {
            'question_text': 'Describe a situation where you had to work with a difficult team member',
            'interview_type': 'behavioral',
            'difficulty_level': 'medium',
            'category': 'teamwork',
            'expected_keywords': ['communication', 'conflict', 'resolution', 'collaboration', 'outcome']
        },
        {
            'question_text': 'What is your greatest professional achievement to date?',
            'interview_type': 'behavioral',
            'difficulty_level': 'easy',
            'category': 'achievements',
            'expected_keywords': ['project', 'impact', 'role', 'success', 'proud']
        },
        {
            'question_text': 'Tell me about a time when you had to learn a new technology quickly',
            'interview_type': 'behavioral',
            'difficulty_level': 'easy',
            'category': 'learning_agility',
            'expected_keywords': ['learning', 'new technology', 'quickly', 'approach', 'application']
        },
        {
            'question_text': 'Describe a time when you had to make a decision with incomplete information',
            'interview_type': 'behavioral',
            'difficulty_level': 'hard',
            'category': 'decision_making',
            'expected_keywords': ['decision', 'incomplete', 'analysis', 'risk', 'outcome']
        },
        {
            'question_text': 'Tell me about a time when you disagreed with your manager',
            'interview_type': 'behavioral',
            'difficulty_level': 'hard',
            'category': 'conflict_resolution',
            'expected_keywords': ['disagreement', 'manager', 'perspective', 'resolution', 'professional']
        },
        {
            'question_text': 'Describe a project where you had to collaborate with multiple stakeholders',
            'interview_type': 'behavioral',
            'difficulty_level': 'medium',
            'category': 'collaboration',
            'expected_keywords': ['stakeholders', 'collaboration', 'communication', 'coordination', 'success']
        },
        {
            'question_text': 'Tell me about a mistake you made and how you handled it',
            'interview_type': 'behavioral',
            'difficulty_level': 'medium',
            'category': 'accountability',
            'expected_keywords': ['mistake', 'responsibility', 'corrective action', 'learning', 'prevention']
        }
    ]
    
    # Company-specific questions (Google)
    google_questions = [
        {
            'question_text': 'How would you find the kth largest element in an unsorted array?',
            'interview_type': 'technical_software',
            'difficulty_level': 'hard',
            'company': 'google',
            'category': 'algorithms',
            'expected_keywords': ['quickselect', 'heap', 'partition', 'O(n)', 'average']
        },
        {
            'question_text': 'Design a recommendation system for YouTube videos',
            'interview_type': 'technical_software',
            'difficulty_level': 'hard', 
            'company': 'google',
            'category': 'system_design',
            'expected_keywords': ['collaborative filtering', 'machine learning', 'scalability', 'personalization']
        },
        {
            'question_text': 'Why do you want to work at Google?',
            'interview_type': 'behavioral',
            'difficulty_level': 'easy',
            'company': 'google',
            'category': 'company_fit',
            'expected_keywords': ['innovation', 'scale', 'impact', 'technology', 'mission']
        }
    ]
    
    # Amazon questions
    amazon_questions = [
        {
            'question_text': 'Design a distributed cache system',
            'interview_type': 'technical_software',
            'difficulty_level': 'hard',
            'company': 'amazon',
            'category': 'system_design',
            'expected_keywords': ['distributed', 'cache', 'consistency', 'sharding', 'replication']
        },
        {
            'question_text': 'Tell me about a time when you had to work with limited resources',
            'interview_type': 'behavioral',
            'difficulty_level': 'medium',
            'company': 'amazon',
            'category': 'frugality',
            'expected_keywords': ['limited resources', 'creativity', 'efficiency', 'priorities', 'outcome']
        }
    ]
    
    # Combine all questions
    all_questions = technical_questions + behavioral_questions + google_questions + amazon_questions
    
    # Add to database
    for q_data in all_questions:
        question = InterviewQuestion(**q_data)
        db.add(question)
    
    db.commit()
    db.close()
    print(f"Seeded {len(all_questions)} questions successfully")

if __name__ == '__main__':
    init_database()
    seed_questions()
