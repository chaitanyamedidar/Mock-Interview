import { useState, useEffect, useCallback } from 'react';
import { 
  apiService, 
  InterviewQuestion, 
  InterviewSession, 
  ResponseAnalysis,
  InterviewType,
  DifficultyLevel 
} from '@/lib/api';

export interface InterviewState {
  session: InterviewSession | null;
  questions: InterviewQuestion[];
  currentQuestionIndex: number;
  responses: Array<{
    question: InterviewQuestion;
    response_text: string;
    analysis?: ResponseAnalysis;
  }>;
  isLoading: boolean;
  error: string | null;
  isStarted: boolean;
  isCompleted: boolean;
}

const initialState: InterviewState = {
  session: null,
  questions: [],
  currentQuestionIndex: 0,
  responses: [],
  isLoading: false,
  error: null,
  isStarted: false,
  isCompleted: false,
};

export const useInterview = () => {
  const [state, setState] = useState<InterviewState>(initialState);

  const setLoading = (loading: boolean) => {
    setState(prev => ({ ...prev, isLoading: loading }));
  };

  const setError = (error: string | null) => {
    setState(prev => ({ ...prev, error }));
  };

  const startInterview = useCallback(async (params: {
    interview_type: InterviewType;
    difficulty: DifficultyLevel;
    duration: number;
    company?: string;
  }) => {
    setLoading(true);
    setError(null);

    try {
      const result = await apiService.startInterview(params);
      
      setState(prev => ({
        ...prev,
        session: {
          session_id: result.session_id,
          interview_type: params.interview_type,
          difficulty_level: params.difficulty,
          company: params.company,
          duration_minutes: params.duration,
          status: result.status,
          started_at: new Date().toISOString(),
          assistant_id: result.assistant_id,
          vapi_config: result.vapi_config,
        },
        questions: result.questions,
        isStarted: true,
        isLoading: false,
      }));

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to start interview';
      setError(errorMessage);
      setLoading(false);
      throw error;
    }
  }, []);

  const nextQuestion = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentQuestionIndex: prev.currentQuestionIndex + 1,
    }));
  }, []);

  const endInterview = useCallback(async () => {
    if (!state.session) {
      throw new Error('No active session');
    }

    setLoading(true);
    setError(null);

    try {
      const feedback = await apiService.endInterview(state.session.session_id);
      
      setState(prev => ({
        ...prev,
        isCompleted: true,
        isLoading: false,
      }));

      return feedback;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Failed to end interview';
      setError(errorMessage);
      setLoading(false);
      throw error;
    }
  }, [state.session]);

  const resetInterview = useCallback(() => {
    setState(initialState);
  }, []);

  const getCurrentQuestion = useCallback(() => {
    if (state.currentQuestionIndex < state.questions.length) {
      return state.questions[state.currentQuestionIndex];
    }
    return null;
  }, [state.questions, state.currentQuestionIndex]);

  const getProgress = useCallback(() => {
    if (state.questions.length === 0) return 0;
    return ((state.currentQuestionIndex + 1) / state.questions.length) * 100;
  }, [state.questions.length, state.currentQuestionIndex]);

  const isLastQuestion = useCallback(() => {
    return state.currentQuestionIndex >= state.questions.length - 1;
  }, [state.currentQuestionIndex, state.questions.length]);

  return {
    ...state,
    startInterview,
    nextQuestion,
    endInterview,
    resetInterview,
    getCurrentQuestion,
    getProgress,
    isLastQuestion,
  };
};