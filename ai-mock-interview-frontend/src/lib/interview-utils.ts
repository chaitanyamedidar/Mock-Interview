import { 
  InterviewDataset, 
  TechnicalQuestion, 
  BehavioralQuestion, 
  CodingChallenge,
  QuestionFilter,
  QuestionType,
  DifficultyLevel 
} from '../types/interview';
import interviewData from '../data/interview-questions.json';

const dataset = interviewData as InterviewDataset;

/**
 * Get all questions from the dataset
 */
export function getAllQuestions(): (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[] {
  const allQuestions: (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[] = [];
  
  // Technical questions
  Object.values(dataset.technical_questions.computer_science).forEach(categoryQuestions => {
    allQuestions.push(...categoryQuestions);
  });
  
  Object.values(dataset.technical_questions.programming_languages).forEach(languageQuestions => {
    allQuestions.push(...languageQuestions);
  });
  
  allQuestions.push(...dataset.technical_questions.system_design);
  
  // Behavioral questions
  Object.values(dataset.behavioral_questions).forEach(categoryQuestions => {
    allQuestions.push(...categoryQuestions);
  });
  
  // Coding challenges
  Object.values(dataset.coding_challenges).forEach(difficultyQuestions => {
    allQuestions.push(...difficultyQuestions);
  });
  
  return allQuestions;
}

/**
 * Filter questions based on criteria
 */
export function filterQuestions(
  filter: QuestionFilter
): (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[] {
  const allQuestions = getAllQuestions();
  
  return allQuestions.filter(question => {
    // Filter by difficulty
    if (filter.difficulty && question.difficulty !== filter.difficulty) {
      return false;
    }
    
    // Filter by topics (for technical questions and coding challenges)
    if (filter.topics && filter.topics.length > 0) {
      if ('topics' in question) {
        const hasMatchingTopic = filter.topics.some(topic => 
          question.topics.some(qTopic => 
            qTopic.toLowerCase().includes(topic.toLowerCase())
          )
        );
        if (!hasMatchingTopic) return false;
      }
    }
    
    // Filter by category (for behavioral questions)
    if (filter.category && 'category' in question) {
      if (!question.category.toLowerCase().includes(filter.category.toLowerCase())) {
        return false;
      }
    }
    
    return true;
  });
}

/**
 * Get random questions based on filter criteria
 */
export function getRandomQuestions(
  filter: QuestionFilter,
  count: number = 5
): (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[] {
  const filteredQuestions = filterQuestions(filter);
  
  if (filteredQuestions.length <= count) {
    return filteredQuestions;
  }
  
  const shuffled = [...filteredQuestions].sort(() => 0.5 - Math.random());
  return shuffled.slice(0, count);
}

/**
 * Get questions by specific type
 */
export function getQuestionsByType(type: QuestionType): (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[] {
  switch (type) {
    case 'technical':
      const technicalQuestions: TechnicalQuestion[] = [];
      Object.values(dataset.technical_questions.computer_science).forEach(categoryQuestions => {
        technicalQuestions.push(...categoryQuestions);
      });
      Object.values(dataset.technical_questions.programming_languages).forEach(languageQuestions => {
        technicalQuestions.push(...languageQuestions);
      });
      technicalQuestions.push(...dataset.technical_questions.system_design);
      return technicalQuestions;
      
    case 'behavioral':
      const behavioralQuestions: BehavioralQuestion[] = [];
      Object.values(dataset.behavioral_questions).forEach(categoryQuestions => {
        behavioralQuestions.push(...categoryQuestions);
      });
      return behavioralQuestions;
      
    case 'coding':
      const codingQuestions: CodingChallenge[] = [];
      Object.values(dataset.coding_challenges).forEach(difficultyQuestions => {
        codingQuestions.push(...difficultyQuestions);
      });
      return codingQuestions;
      
    default:
      return [];
  }
}

/**
 * Get questions by difficulty level
 */
export function getQuestionsByDifficulty(difficulty: DifficultyLevel): (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[] {
  return getAllQuestions().filter(question => question.difficulty === difficulty);
}

/**
 * Search questions by keywords
 */
export function searchQuestions(
  keywords: string[]
): (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[] {
  const allQuestions = getAllQuestions();
  
  return allQuestions.filter(question => {
    const questionText = question.question.toLowerCase();
    
    return keywords.some(keyword => 
      questionText.includes(keyword.toLowerCase()) ||
      ('topics' in question && question.topics.some(topic => 
        topic.toLowerCase().includes(keyword.toLowerCase())
      )) ||
      ('category' in question && question.category.toLowerCase().includes(keyword.toLowerCase()))
    );
  });
}

/**
 * Get interview questions for a complete session
 */
export function generateInterviewSession(
  type: QuestionType,
  difficulty: DifficultyLevel,
  duration: number = 45 // minutes
): (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[] {
  const questionsPerMinute = type === 'coding' ? 0.5 : 1; // Coding questions take longer
  const targetQuestionCount = Math.floor(duration * questionsPerMinute);
  
  const filter: QuestionFilter = {
    type,
    difficulty
  };
  
  return getRandomQuestions(filter, targetQuestionCount);
}

/**
 * Get follow-up questions for a given question
 */
export function getFollowUpQuestion(questionId: string): string | null {
  const allQuestions = getAllQuestions();
  const question = allQuestions.find(q => q.id === questionId);
  
  if (question && 'follow_up' in question) {
    return question.follow_up || null;
  }
  
  return null;
}

/**
 * Get tips for behavioral questions
 */
export function getBehavioralTips(questionId: string): string[] {
  const behavioralQuestions = getQuestionsByType('behavioral') as BehavioralQuestion[];
  const question = behavioralQuestions.find(q => q.id === questionId);
  
  return question?.tips || [];
}

/**
 * Get question statistics
 */
export function getQuestionStats() {
  const allQuestions = getAllQuestions();
  
  const stats = {
    total: allQuestions.length,
    byType: {
      technical: getQuestionsByType('technical').length,
      behavioral: getQuestionsByType('behavioral').length,
      coding: getQuestionsByType('coding').length,
    },
    byDifficulty: {
      easy: getQuestionsByDifficulty('easy').length,
      medium: getQuestionsByDifficulty('medium').length,
      hard: getQuestionsByDifficulty('hard').length,
    }
  };
  
  return stats;
}

/**
 * Validate question format
 */
export function validateQuestion(question: any): boolean {
  const requiredFields = ['id', 'question', 'difficulty'];
  
  for (const field of requiredFields) {
    if (!question[field]) {
      return false;
    }
  }
  
  if (!['easy', 'medium', 'hard'].includes(question.difficulty)) {
    return false;
  }
  
  return true;
}

export { dataset };