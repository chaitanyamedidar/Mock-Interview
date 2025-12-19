'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, AlertCircle, TrendingUp, MessageSquare } from 'lucide-react';

interface FeedbackDisplayProps {
  feedback?: {
    overall_score?: number;
    strengths?: string[];
    areas_for_improvement?: string[];
    suggestions?: string[];
    detailed_metrics?: {
      clarity?: number;
      relevance?: number;
      structure?: number;
      confidence?: number;
    };
  };
  transcript: string;
  isAnalyzing: boolean;
}

export default function FeedbackDisplay({ feedback, transcript, isAnalyzing }: FeedbackDisplayProps) {
  if (!transcript && !feedback) {
    return (
      <Card className="bg-card/50 border-border/40">
        <CardContent className="p-6">
          <div className="flex items-center justify-center h-32 text-muted-foreground">
            <div className="text-center space-y-2">
              <MessageSquare className="h-8 w-8 mx-auto opacity-20" />
              <p className="text-sm">Your response and AI feedback will appear here</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Transcript */}
      {transcript && (
        <Card className="bg-card/50 border-border/40">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <MessageSquare className="h-4 w-4" />
              Your Response
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm leading-relaxed bg-muted/30 p-3 rounded">
              {transcript}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Analysis Status */}
      {isAnalyzing && (
        <Card className="bg-blue-50/50 border-blue-200/50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2">
              <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full" />
              <p className="text-sm text-blue-700">Analyzing your response with AI...</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* AI Feedback */}
      {feedback && (
        <Card className="bg-card/50 border-border/40">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <CheckCircle className="h-4 w-4 text-green-500" />
              AI Feedback
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Overall Score */}
            {feedback.overall_score && (
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium">Overall Score:</span>
                <Badge variant={feedback.overall_score >= 7 ? "default" : "secondary"}>
                  {feedback.overall_score}/10
                </Badge>
              </div>
            )}

            {/* Detailed Metrics */}
            {feedback.detailed_metrics && (
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(feedback.detailed_metrics).map(([metric, score]) => (
                  <div key={metric} className="flex justify-between items-center text-sm">
                    <span className="capitalize">{metric}:</span>
                    <Badge variant="outline">{score}/10</Badge>
                  </div>
                ))}
              </div>
            )}

            {/* Strengths */}
            {feedback.strengths && feedback.strengths.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-green-600 mb-2">Strengths:</h4>
                <ul className="space-y-1">
                  {feedback.strengths.map((strength, index) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <CheckCircle className="h-3 w-3 text-green-500 mt-0.5 flex-shrink-0" />
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Areas for Improvement */}
            {feedback.areas_for_improvement && feedback.areas_for_improvement.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-orange-600 mb-2">Areas for Improvement:</h4>
                <ul className="space-y-1">
                  {feedback.areas_for_improvement.map((area, index) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <AlertCircle className="h-3 w-3 text-orange-500 mt-0.5 flex-shrink-0" />
                      {area}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suggestions */}
            {feedback.suggestions && feedback.suggestions.length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-blue-600 mb-2">Suggestions:</h4>
                <ul className="space-y-1">
                  {feedback.suggestions.map((suggestion, index) => (
                    <li key={index} className="text-sm flex items-start gap-2">
                      <TrendingUp className="h-3 w-3 text-blue-500 mt-0.5 flex-shrink-0" />
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}