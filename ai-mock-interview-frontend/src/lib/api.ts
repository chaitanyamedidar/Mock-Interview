// API service for AI Mock Interview Backend
const API_BASE_URL = 'http://localhost:8000';

export enum InterviewType {
  TECHNICAL = 'technical',
  BEHAVIORAL = 'behavioral',
  SYSTEM_DESIGN = 'system-design',
  CODING = 'coding'
}

export enum DifficultyLevel {
  EASY = 'easy',
  INTERMEDIATE = 'medium',
  HARD = 'hard'
}

export interface InterviewSession {
  session_id: string;
  interview_type: string;
  difficulty_level: string;
  company?: string;
  duration_minutes: number;
  status: string;
  started_at: string;
  overall_score?: number;
  overall_rating?: string;
}

export interface InterviewQuestion {
  question_id: number;
  question_text: string;
  interview_type: string;
  difficulty_level: string;
  company?: string;
  category: string;
  expected_keywords: string[];
}

export interface ResponseAnalysis {
  overall_score: number;
  rating: string;
  scores: {
    content_quality: number;
    communication: number;
    confidence: number;
    technical_accuracy: number;
  };
  features: Record<string, any>;
  feedback_suggestions: Array<{
    type: 'strength' | 'improvement';
    category: string;
    message: string;
  }>;
}

export interface FeedbackResponse {
  session_id: string;
  overall_score: number;
  overall_rating: string;
  detailed_feedback: Array<{
    question_number: number;
    question_text: string;
    user_response: string;
    analysis: ResponseAnalysis;
  }>;
  improvement_recommendations: string[];
  strengths: string[];
  areas_for_improvement: string[];
}

class APIService {
  private async fetchAPI(endpoint: string, options: RequestInit = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP ${response.status}: ${response.statusText}`);
    }

    return response.json();
  }

  // Start a new interview session
  async startInterview(params: {
    interview_type: InterviewType;
    difficulty: DifficultyLevel;
    duration: number;
    company?: string;
  }): Promise<{
    session_id: string;
    status: string;
    questions: InterviewQuestion[];
    vapi_call_url?: string;
  }> {
    return this.fetchAPI('/api/interview/start', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // Get questions for specific interview type
  async getQuestions(
    interviewType: string,
    difficulty?: string,
    company?: string,
    limit: number = 10
  ): Promise<{
    questions: InterviewQuestion[];
    total_count: number;
  }> {
    const params = new URLSearchParams();
    if (difficulty) params.append('difficulty', difficulty);
    if (company) params.append('company', company);
    params.append('limit', limit.toString());

    return this.fetchAPI(`/api/questions/${interviewType}?${params.toString()}`);
  }

  // Analyze a response
  async analyzeResponse(params: {
    session_id: string;
    question_number: number;
    question: string;
    response: string;
    interview_type: string;
  }): Promise<ResponseAnalysis> {
    return this.fetchAPI('/api/interview/analyze-response', {
      method: 'POST',
      body: JSON.stringify(params),
    });
  }

  // End interview and get feedback
  async endInterview(sessionId: string): Promise<FeedbackResponse> {
    return this.fetchAPI('/api/interview/end', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId }),
    });
  }

  // Get session details
  async getSession(sessionId: string): Promise<InterviewSession> {
    return this.fetchAPI(`/api/session/${sessionId}`);
  }

  // Health check
  async healthCheck(): Promise<{ status: string; message: string; version: string }> {
    return this.fetchAPI('/');
  }
}

export const apiService = new APIService();

export type InterviewStatus = 'not_started' | 'in_progress' | 'completed' | 'abandoned';

// Helper functions
export const formatInterviewType = (type: InterviewType): string => {
  const typeMap: Record<InterviewType, string> = {
    [InterviewType.TECHNICAL]: 'Technical',
    [InterviewType.BEHAVIORAL]: 'Behavioral',
    [InterviewType.SYSTEM_DESIGN]: 'System Design',
    [InterviewType.CODING]: 'Coding',
  };
  return typeMap[type] || type;
};

export const formatDifficulty = (difficulty: DifficultyLevel): string => {
  const difficultyMap: Record<DifficultyLevel, string> = {
    [DifficultyLevel.EASY]: 'Easy',
    [DifficultyLevel.INTERMEDIATE]: 'Intermediate',
    [DifficultyLevel.HARD]: 'Hard',
  };
  return difficultyMap[difficulty] || difficulty;
};

export const getRatingColor = (rating: string): string => {
  const colorMap: Record<string, string> = {
    'excellent': 'text-green-600 bg-green-100',
    'good': 'text-blue-600 bg-blue-100',
    'average': 'text-yellow-600 bg-yellow-100',
    'poor': 'text-red-600 bg-red-100',
  };
  return colorMap[rating.toLowerCase()] || 'text-gray-600 bg-gray-100';
};

export const getScoreColor = (score: number): string => {
  if (score >= 8) return 'text-green-600';
  if (score >= 6) return 'text-blue-600';
  if (score >= 4) return 'text-yellow-600';
  return 'text-red-600';
};