// Types for the interview questions dataset

export interface TechnicalQuestion {
  id: string;
  question: string;
  difficulty: 'easy' | 'medium' | 'hard';
  topics: string[];
  follow_up?: string;
}

export interface BehavioralQuestion {
  id: string;
  question: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  tips: string[];
}

export interface CodingChallenge {
  id: string;
  question: string;
  difficulty: 'easy' | 'medium' | 'hard';
  topics: string[];
  sample_input: string;
  expected_output: string;
  follow_up?: string;
}

export interface QuestionCategory {
  [key: string]: TechnicalQuestion[] | BehavioralQuestion[] | CodingChallenge[];
}

export interface InterviewDataset {
  technical_questions: {
    computer_science: {
      programming_fundamentals: TechnicalQuestion[];
      object_oriented_programming: TechnicalQuestion[];
      databases: TechnicalQuestion[];
      web_development: TechnicalQuestion[];
    };
    programming_languages: {
      javascript: TechnicalQuestion[];
      python: TechnicalQuestion[];
      java: TechnicalQuestion[];
    };
    system_design: TechnicalQuestion[];
  };
  behavioral_questions: {
    leadership_and_teamwork: BehavioralQuestion[];
    problem_solving: BehavioralQuestion[];
    adaptability_and_learning: BehavioralQuestion[];
    communication: BehavioralQuestion[];
    failure_and_challenges: BehavioralQuestion[];
    motivation_and_goals: BehavioralQuestion[];
    company_specific: BehavioralQuestion[];
  };
  coding_challenges: {
    easy: CodingChallenge[];
    medium: CodingChallenge[];
    hard: CodingChallenge[];
  };
  metadata: {
    total_questions: number;
    categories: string[];
    difficulty_levels: string[];
    tags: string[];
    last_updated: string;
    version: string;
  };
}

// Utility types for filtering and searching
export type QuestionType = 'technical' | 'behavioral' | 'coding';
export type DifficultyLevel = 'easy' | 'medium' | 'hard';

export interface QuestionFilter {
  type?: QuestionType;
  difficulty?: DifficultyLevel;
  topics?: string[];
  category?: string;
}

export interface InterviewSession {
  id: string;
  studentName: string;
  sessionType: QuestionType;
  difficulty: DifficultyLevel;
  duration: number; // in minutes
  questions: (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[];
  startTime: Date;
  endTime?: Date;
  responses?: SessionResponse[];
}

export interface SessionResponse {
  questionId: string;
  response: string;
  timeSpent: number; // in seconds
  score?: number; // 1-10 scale
  feedback?: string;
}

// Helper functions type definitions
export type QuestionSelector = (
  dataset: InterviewDataset,
  filter: QuestionFilter,
  count: number
) => (TechnicalQuestion | BehavioralQuestion | CodingChallenge)[];

export type FeedbackGenerator = (
  question: TechnicalQuestion | BehavioralQuestion | CodingChallenge,
  response: string
) => {
  score: number;
  feedback: string;
  suggestions: string[];
};