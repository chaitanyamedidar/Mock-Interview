"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  TrendingUp,
  TrendingDown,
  Award,
  Target,
  Clock,
  MessageSquare,
  Sparkles,
  CheckCircle2,
  AlertCircle,
  Home,
  Download,
  Share2,
  Loader2,
  Code2,
  Zap,
  BookOpen
} from "lucide-react";
import Link from "next/link";
import { getScoreColor as getScoreColorUtil } from "@/lib/api";

// Interfaces matching backend response
interface AnalysisData {
  report_summary: {
    overall_score: number;
    performance_label: string;
    total_questions_analyzed: number;
    categories: {
      [key: string]: {
        score: number;
        trend: string;
      };
    };
  };
  ai_recommendations: Array<{
    title: string;
    description: string;
  }>;
  questions_breakdown: Array<{
    question: string;
    answer: string;
    score: number;
    strengths: string[];
    improvements: string[];
  }>;
  metadata: any;
}

interface TechnicalData {
  session_id: string;
  question_title: string;
  question_description: string;
  code: string;
  language: string;
  overall_score: number;
  scores: {
    correctness?: number;
    code_quality?: number;
    efficiency?: number;
    best_practices?: number;
  };
  time_complexity: string;
  space_complexity: string;
  strengths: string[];
  improvements: string[];
  feedback: string;
}

export default function FeedbackPage() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get('session_id');

  const [data, setData] = useState<AnalysisData | null>(null);
  const [technicalData, setTechnicalData] = useState<TechnicalData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedQuestion, setSelectedQuestion] = useState(0);
  const [activeRound, setActiveRound] = useState<"round1" | "round2">("round1");

  useEffect(() => {
    if (!sessionId) {
      setError("No session ID provided");
      setLoading(false);
      return;
    }

    const fetchAllData = async () => {
      try {
        // Fetch Round 1 (Behavioral) results
        const behavioralResponse = await fetch(`http://localhost:8000/api/v1/interview/results/${sessionId}`);
        if (behavioralResponse.ok) {
          const result = await behavioralResponse.json();
          if (behavioralResponse.status !== 202) {
            setData(result);
          }
        }

        // Fetch Round 2 (Technical) results
        const technicalResponse = await fetch(`http://localhost:8000/api/v1/technical/results/${sessionId}`);
        if (technicalResponse.ok) {
          const techResult = await technicalResponse.json();
          setTechnicalData(techResult);
        }

        setLoading(false);
      } catch (err: any) {
        console.error("Error fetching data:", err);
        setError(err.message);
        setLoading(false);
      }
    };

    fetchAllData();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary mb-4" />
          <h2 className="text-xl font-semibold">Analyzing your interview...</h2>
          <p className="text-muted-foreground mt-2">Gathering insights from your responses.</p>
        </div>
      </div>
    );
  }

  if (error && !data && !technicalData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle className="text-destructive">Error Loading Results</CardTitle>
          </CardHeader>
          <CardContent>
            <p>{error}</p>
            <Link href="/">
              <Button className="mt-4 w-full">Return Home</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!data && !technicalData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Card className="max-w-md w-full">
          <CardHeader>
            <CardTitle>No Results Found</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">No interview data found for this session.</p>
            <Link href="/">
              <Button className="mt-4 w-full">Return Home</Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    );
  }

  const report_summary = data?.report_summary;
  const questions_breakdown = data?.questions_breakdown;
  const ai_recommendations = data?.ai_recommendations;
  
  const metrics = [
    { label: "Communication", key: "communication", icon: MessageSquare },
    { label: "Technical Skills", key: "technical_skills", icon: Target },
    { label: "Problem Solving", key: "problem_solving", icon: Sparkles },
    { label: "Time Management", key: "time_management", icon: Clock },
  ];

  const technicalMetrics = [
    { label: "Correctness", key: "correctness", icon: CheckCircle2 },
    { label: "Code Quality", key: "code_quality", icon: Code2 },
    { label: "Efficiency", key: "efficiency", icon: Zap },
    { label: "Best Practices", key: "best_practices", icon: BookOpen },
  ];

  const getScoreColor = (score: number) => {
    if (score >= 85) return "text-green-500";
    if (score >= 70) return "text-yellow-500";
    return "text-red-500";
  };

  const getScoreBgColor = (score: number) => {
    if (score >= 85) return "bg-green-500/10 border-green-500/20";
    if (score >= 70) return "bg-yellow-500/10 border-yellow-500/20";
    return "bg-red-500/10 border-red-500/20";
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/40 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">InterviewAI</span>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" size="sm">
              <Share2 className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Overall Score Section */}
        <div className="text-center mb-12">
          <Badge variant="secondary" className="mb-4">
            <Award className="h-3 w-3 mr-1" />
            Interview Complete
          </Badge>
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Your Performance Report</h1>
          <p className="text-muted-foreground text-lg">
            {report_summary?.performance_label || "Complete"}! Here's how you did.
          </p>
        </div>

        {/* Round Selection Tabs */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex rounded-lg border border-border/40 p-1 bg-muted/30">
            <button
              onClick={() => setActiveRound("round1")}
              className={`px-6 py-3 rounded-md text-sm font-medium transition-all ${
                activeRound === "round1"
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <MessageSquare className="h-4 w-4 inline mr-2" />
              Round 1 - Behavioral
              {data && <Badge variant="secondary" className="ml-2">{Math.round(report_summary?.overall_score || 0)}</Badge>}
            </button>
            <button
              onClick={() => setActiveRound("round2")}
              className={`px-6 py-3 rounded-md text-sm font-medium transition-all ${
                activeRound === "round2"
                  ? "bg-primary text-primary-foreground shadow-sm"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              <Code2 className="h-4 w-4 inline mr-2" />
              Round 2 - Technical
              {technicalData && <Badge variant="secondary" className="ml-2">{Math.round(technicalData.overall_score)}</Badge>}
            </button>
          </div>
        </div>

        {/* Round 1 - Behavioral Content */}
        {activeRound === "round1" && data && report_summary && (
          <>
            {/* Overall Score Card */}
            <Card className="bg-gradient-to-br from-primary/10 to-purple-600/10 border-primary/20 mb-8">
              <CardContent className="p-8">
                <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                  <div className="flex-1 text-center md:text-left">
                    <h2 className="text-2xl font-bold mb-2">Behavioral Interview Score</h2>
                    <p className="text-muted-foreground mb-4">
                      Based on {report_summary.total_questions_analyzed} questions analyzed
                    </p>
                    <div className="flex items-center gap-4 justify-center md:justify-start">
                      <div className={`text-6xl font-bold ${getScoreColor(report_summary.overall_score)}`}>
                        {Math.round(report_summary.overall_score)}
                      </div>
                      <div className="text-left">
                        <div className="text-2xl font-bold text-muted-foreground">/100</div>
                        <Badge className="bg-green-500/20 text-green-500 border-green-500/30">
                          <TrendingUp className="h-3 w-3 mr-1" />
                          {report_summary.performance_label}
                        </Badge>
                      </div>
                    </div>
              </div>
              <div className="flex-1 w-full">
                <div className="grid grid-cols-2 gap-4">
                  {metrics.map((metric, index) => {
                    const category = report_summary.categories[metric.key];
                    return (
                      <div key={index} className="bg-background/50 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <metric.icon className="h-4 w-4 text-primary" />
                          <span className="text-sm font-medium">{metric.label}</span>
                        </div>
                        {category && (
                          <>
                            <div className="flex items-center gap-2">
                              <span className={`text-2xl font-bold ${getScoreColor(category.score)}`}>
                                {category.score}
                              </span>
                              {category.trend === "up" ? (
                                <TrendingUp className="h-4 w-4 text-green-500" />
                              ) : (
                                <TrendingDown className="h-4 w-4 text-yellow-500" />
                              )}
                            </div>
                            <Progress value={category.score} className="h-1.5 mt-2" />
                          </>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Detailed Feedback */}
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Question List */}
          <div className="lg:col-span-1">
            <Card className="bg-card/50 border-border/40">
              <CardHeader>
                <CardTitle>Questions</CardTitle>
                <CardDescription>Click to view detailed feedback</CardDescription>
              </CardHeader>
              <CardContent className="p-0">
                <div className="space-y-1">
                  {questions_breakdown && questions_breakdown.map((item, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedQuestion(index)}
                      className={`w-full text-left p-4 transition-colors border-l-2 ${selectedQuestion === index
                          ? "bg-primary/10 border-primary"
                          : "border-transparent hover:bg-muted/50"
                        }`}
                    >
                      <div className="flex items-start justify-between gap-3">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-xs font-medium text-muted-foreground">
                              Q{index + 1}
                            </span>
                            <Badge
                              variant="secondary"
                              className={`text-xs ${getScoreBgColor(item.score)}`}
                            >
                              {item.score}
                            </Badge>
                          </div>
                          <p className="text-sm font-medium line-clamp-2">
                            {item.question}
                          </p>
                        </div>
                      </div>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Question Details */}
          <div className="lg:col-span-2 space-y-6">
            {questions_breakdown && questions_breakdown[selectedQuestion] && (
              <Card className="bg-card/50 border-border/40">
                <CardHeader>
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <Badge variant="secondary">Question {selectedQuestion + 1}</Badge>
                        <Badge className={getScoreBgColor(questions_breakdown[selectedQuestion].score)}>
                          Score: {questions_breakdown[selectedQuestion].score}/100
                        </Badge>
                      </div>
                      <CardTitle className="text-xl">
                        {questions_breakdown[selectedQuestion].question}
                      </CardTitle>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="space-y-6">
                  <Tabs defaultValue="feedback" className="w-full">
                    <TabsList className="grid w-full grid-cols-2">
                      <TabsTrigger value="feedback">Feedback</TabsTrigger>
                      <TabsTrigger value="transcript">Your Answer</TabsTrigger>
                    </TabsList>
                    <TabsContent value="feedback" className="space-y-6 mt-6">
                      {/* Strengths */}
                      {questions_breakdown[selectedQuestion].strengths?.length > 0 && (
                        <div>
                          <div className="flex items-center gap-2 mb-3">
                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                            <h3 className="font-semibold">Strengths</h3>
                          </div>
                          <div className="space-y-2">
                            {questions_breakdown[selectedQuestion].strengths.map((strength, idx) => (
                              <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                                <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                                <p className="text-sm">{strength}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Areas for Improvement */}
                      {questions_breakdown[selectedQuestion].improvements?.length > 0 && (
                        <div>
                          <div className="flex items-center gap-2 mb-3">
                            <AlertCircle className="h-5 w-5 text-yellow-500" />
                            <h3 className="font-semibold">Areas for Improvement</h3>
                          </div>
                          <div className="space-y-2">
                            {questions_breakdown[selectedQuestion].improvements.map((improvement, idx) => (
                              <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                                <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                                <p className="text-sm">{improvement}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </TabsContent>
                    <TabsContent value="transcript" className="mt-6">
                      <div className="bg-muted/30 rounded-lg p-6">
                        <p className="text-sm leading-relaxed">
                          {questions_breakdown[selectedQuestion].answer}
                        </p>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            )}

            {/* AI Recommendations */}
            <Card className="bg-gradient-to-br from-primary/5 to-purple-600/5 border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  AI Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {ai_recommendations && ai_recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start gap-3">
                    <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-xs font-bold text-primary">{index + 1}</span>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">{rec.title}</h4>
                      <p className="text-sm text-muted-foreground">
                        {rec.description}
                      </p>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </div>
          </>
        )}

        {/* Round 1 - No Data State */}
        {activeRound === "round1" && !data && (
          <Card className="bg-card/50 border-border/40">
            <CardContent className="p-12 text-center">
              <MessageSquare className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-xl font-semibold mb-2">No Behavioral Interview Data</h3>
              <p className="text-muted-foreground">Round 1 results are not available for this session.</p>
            </CardContent>
          </Card>
        )}

        {/* Round 2 - Technical Content */}
        {activeRound === "round2" && technicalData && (
          <>
            {/* Technical Score Card */}
            <Card className="bg-gradient-to-br from-blue-500/10 to-cyan-600/10 border-blue-500/20 mb-8">
              <CardContent className="p-8">
                <div className="flex flex-col md:flex-row items-center justify-between gap-8">
                  <div className="flex-1 text-center md:text-left">
                    <h2 className="text-2xl font-bold mb-2">Technical Interview Score</h2>
                    <p className="text-muted-foreground mb-4">
                      Code evaluation for: {technicalData.question_title}
                    </p>
                    <div className="flex items-center gap-4 justify-center md:justify-start">
                      <div className={`text-6xl font-bold ${getScoreColor(technicalData.overall_score)}`}>
                        {Math.round(technicalData.overall_score)}
                      </div>
                      <div className="text-left">
                        <div className="text-2xl font-bold text-muted-foreground">/100</div>
                        <Badge className={getScoreBgColor(technicalData.overall_score)}>
                          <Code2 className="h-3 w-3 mr-1" />
                          {technicalData.overall_score >= 85 ? "Excellent" : technicalData.overall_score >= 70 ? "Good" : "Needs Improvement"}
                        </Badge>
                      </div>
                    </div>
                  </div>
                  <div className="flex-1 w-full">
                    <div className="grid grid-cols-2 gap-4">
                      {technicalMetrics.map((metric, index) => {
                        const score = technicalData.scores[metric.key as keyof typeof technicalData.scores];
                        return (
                          <div key={index} className="bg-background/50 rounded-lg p-4">
                            <div className="flex items-center gap-2 mb-2">
                              <metric.icon className="h-4 w-4 text-blue-500" />
                              <span className="text-sm font-medium">{metric.label}</span>
                            </div>
                            {score !== undefined && (
                              <>
                                <div className="flex items-center gap-2">
                                  <span className={`text-2xl font-bold ${getScoreColor(score)}`}>
                                    {Math.round(score)}
                                  </span>
                                </div>
                                <Progress value={score} className="h-1.5 mt-2" />
                              </>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Complexity Analysis */}
            <div className="grid md:grid-cols-2 gap-6 mb-8">
              <Card className="bg-card/50 border-border/40">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Clock className="h-5 w-5 text-blue-500" />
                    Time Complexity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-mono font-bold text-blue-500">
                    {technicalData.time_complexity}
                  </div>
                </CardContent>
              </Card>
              <Card className="bg-card/50 border-border/40">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-cyan-500" />
                    Space Complexity
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-3xl font-mono font-bold text-cyan-500">
                    {technicalData.space_complexity}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Code & Feedback Section */}
            <div className="grid lg:grid-cols-2 gap-8">
              {/* Your Code */}
              <Card className="bg-card/50 border-border/40">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Code2 className="h-5 w-5 text-primary" />
                    Your Solution
                  </CardTitle>
                  <CardDescription>
                    Language: {technicalData.language}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="bg-zinc-950 rounded-lg p-4 overflow-x-auto">
                    <pre className="text-sm text-zinc-100 font-mono whitespace-pre-wrap">
                      {technicalData.code}
                    </pre>
                  </div>
                </CardContent>
              </Card>

              {/* Feedback */}
              <div className="space-y-6">
                {/* Strengths */}
                {technicalData.strengths?.length > 0 && (
                  <Card className="bg-card/50 border-border/40">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                        Strengths
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      {technicalData.strengths.map((strength, idx) => (
                        <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                          <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{strength}</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* Areas for Improvement */}
                {technicalData.improvements?.length > 0 && (
                  <Card className="bg-card/50 border-border/40">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <AlertCircle className="h-5 w-5 text-yellow-500" />
                        Areas for Improvement
                      </CardTitle>
                    </CardHeader>
                    <CardContent className="space-y-2">
                      {technicalData.improvements.map((improvement, idx) => (
                        <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                          <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                          <p className="text-sm">{improvement}</p>
                        </div>
                      ))}
                    </CardContent>
                  </Card>
                )}

                {/* AI Feedback Summary */}
                {technicalData.feedback && (
                  <Card className="bg-gradient-to-br from-blue-500/5 to-cyan-600/5 border-blue-500/20">
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <Sparkles className="h-5 w-5 text-blue-500" />
                        AI Feedback Summary
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <p className="text-sm leading-relaxed text-muted-foreground">
                        {technicalData.feedback}
                      </p>
                    </CardContent>
                  </Card>
                )}
              </div>
            </div>
          </>
        )}

        {/* Round 2 - No Data State */}
        {activeRound === "round2" && !technicalData && (
          <Card className="bg-card/50 border-border/40">
            <CardContent className="p-12 text-center">
              <Code2 className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
              <h3 className="text-xl font-semibold mb-2">No Technical Interview Data</h3>
              <p className="text-muted-foreground">Round 2 results are not available for this session.</p>
            </CardContent>
          </Card>
        )}

        {/* Action Buttons */}
        <div className="mt-12 flex flex-col sm:flex-row gap-4 justify-center">
          <Link href="/interview">
            <Button size="lg" className="bg-primary hover:bg-primary/90">
              <Target className="mr-2 h-5 w-5" />
              Practice Again
            </Button>
          </Link>
          <Link href="/">
            <Button size="lg" variant="outline">
              <Home className="mr-2 h-5 w-5" />
              Back to Home
            </Button>
          </Link>
        </div>
      </div>
    </div>
  );
}