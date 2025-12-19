'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  getRandomQuestions, 
  getQuestionsByType, 
  getQuestionStats,
  getBehavioralTips,
  getFollowUpQuestion 
} from '@/lib/interview-utils';
import { 
  TechnicalQuestion, 
  BehavioralQuestion, 
  CodingChallenge,
  QuestionType,
  DifficultyLevel 
} from '@/types/interview';

interface InterviewPracticeProps {
  className?: string;
}

export default function InterviewPractice({ className }: InterviewPracticeProps) {
  const [currentQuestion, setCurrentQuestion] = useState<TechnicalQuestion | BehavioralQuestion | CodingChallenge | null>(null);
  const [questionType, setQuestionType] = useState<QuestionType>('technical');
  const [difficulty, setDifficulty] = useState<DifficultyLevel>('medium');
  const [showAnswer, setShowAnswer] = useState(false);
  const [stats, setStats] = useState<any>(null);
  const [sessionQuestions, setSessionQuestions] = useState<(TechnicalQuestion | BehavioralQuestion | CodingChallenge)[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    setStats(getQuestionStats());
  }, []);

  const generateNewQuestion = () => {
    const questions = getRandomQuestions({ type: questionType, difficulty }, 1);
    if (questions.length > 0) {
      setCurrentQuestion(questions[0]);
      setShowAnswer(false);
    }
  };

  const startSession = () => {
    const questions = getRandomQuestions({ type: questionType, difficulty }, 5);
    setSessionQuestions(questions);
    setCurrentIndex(0);
    if (questions.length > 0) {
      setCurrentQuestion(questions[0]);
      setShowAnswer(false);
    }
  };

  const nextQuestion = () => {
    if (currentIndex < sessionQuestions.length - 1) {
      const nextIndex = currentIndex + 1;
      setCurrentIndex(nextIndex);
      setCurrentQuestion(sessionQuestions[nextIndex]);
      setShowAnswer(false);
    }
  };

  const previousQuestion = () => {
    if (currentIndex > 0) {
      const prevIndex = currentIndex - 1;
      setCurrentIndex(prevIndex);
      setCurrentQuestion(sessionQuestions[prevIndex]);
      setShowAnswer(false);
    }
  };

  const getDifficultyColor = (diff: string) => {
    switch (diff) {
      case 'easy': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'hard': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const renderQuestionDetails = () => {
    if (!currentQuestion) return null;

    const isBehavioral = 'category' in currentQuestion;
    const isCoding = 'sample_input' in currentQuestion;
    const followUp = getFollowUpQuestion(currentQuestion.id);
    const tips = isBehavioral ? getBehavioralTips(currentQuestion.id) : [];

    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 flex-wrap">
          <Badge className={getDifficultyColor(currentQuestion.difficulty)}>
            {currentQuestion.difficulty.toUpperCase()}
          </Badge>
          
          {isBehavioral && (
            <Badge variant="outline">
              {(currentQuestion as BehavioralQuestion).category}
            </Badge>
          )}
          
          {'topics' in currentQuestion && currentQuestion.topics.map((topic, index) => (
            <Badge key={index} variant="secondary">
              {topic}
            </Badge>
          ))}
        </div>

        {isCoding && (
          <div className="bg-gray-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Sample Input:</h4>
            <code className="text-sm">{(currentQuestion as CodingChallenge).sample_input}</code>
            <h4 className="font-semibold mb-2 mt-3">Expected Output:</h4>
            <code className="text-sm">{(currentQuestion as CodingChallenge).expected_output}</code>
          </div>
        )}

        {isBehavioral && tips.length > 0 && showAnswer && (
          <div className="bg-blue-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Tips for answering:</h4>
            <ul className="list-disc list-inside space-y-1">
              {tips.map((tip, index) => (
                <li key={index} className="text-sm">{tip}</li>
              ))}
            </ul>
          </div>
        )}

        {followUp && showAnswer && (
          <div className="bg-purple-50 p-4 rounded-lg">
            <h4 className="font-semibold mb-2">Follow-up Question:</h4>
            <p className="text-sm">{followUp}</p>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className={`max-w-4xl mx-auto p-6 space-y-6 ${className}`}>
      <div className="text-center">
        <h1 className="text-3xl font-bold mb-2">AI Mock Interview Practice</h1>
        <p className="text-gray-600">Practice with real interview questions</p>
      </div>

      {stats && (
        <Card>
          <CardHeader>
            <CardTitle>Question Database Stats</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{stats.total}</div>
                <div className="text-sm text-gray-600">Total Questions</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-600">{stats.byType.technical}</div>
                <div className="text-sm text-gray-600">Technical</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{stats.byType.behavioral}</div>
                <div className="text-sm text-gray-600">Behavioral</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-600">{stats.byType.coding}</div>
                <div className="text-sm text-gray-600">Coding</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Interview Settings</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-2">Question Type</label>
              <Select value={questionType} onValueChange={(value: QuestionType) => setQuestionType(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="technical">Technical</SelectItem>
                  <SelectItem value="behavioral">Behavioral</SelectItem>
                  <SelectItem value="coding">Coding Challenge</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Difficulty Level</label>
              <Select value={difficulty} onValueChange={(value: DifficultyLevel) => setDifficulty(value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="easy">Easy</SelectItem>
                  <SelectItem value="medium">Medium</SelectItem>
                  <SelectItem value="hard">Hard</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex gap-2 flex-wrap">
            <Button onClick={generateNewQuestion}>
              Generate Single Question
            </Button>
            <Button onClick={startSession} variant="outline">
              Start 5-Question Session
            </Button>
          </div>
        </CardContent>
      </Card>

      {currentQuestion && (
        <Card>
          <CardHeader>
            <div className="flex justify-between items-start">
              <CardTitle>
                {sessionQuestions.length > 0 && (
                  <span className="text-sm text-gray-500 block">
                    Question {currentIndex + 1} of {sessionQuestions.length}
                  </span>
                )}
                Interview Question
              </CardTitle>
              <Badge variant="outline">ID: {currentQuestion.id}</Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="text-lg font-medium leading-relaxed">
              {currentQuestion.question}
            </div>
            
            {renderQuestionDetails()}

            <div className="flex gap-2 flex-wrap">
              <Button 
                onClick={() => setShowAnswer(!showAnswer)}
                variant={showAnswer ? "secondary" : "default"}
              >
                {showAnswer ? "Hide Hints" : "Show Hints"}
              </Button>
              
              {sessionQuestions.length > 0 && (
                <>
                  <Button 
                    onClick={previousQuestion} 
                    disabled={currentIndex === 0}
                    variant="outline"
                  >
                    Previous
                  </Button>
                  <Button 
                    onClick={nextQuestion} 
                    disabled={currentIndex === sessionQuestions.length - 1}
                    variant="outline"
                  >
                    Next
                  </Button>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}