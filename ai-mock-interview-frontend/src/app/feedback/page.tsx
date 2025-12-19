"use client";

import { useState } from "react";
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
  Share2
} from "lucide-react";
import Link from "next/link";

const overallScore = 82;
const metrics = [
  { label: "Communication", score: 85, icon: MessageSquare, trend: "up" },
  { label: "Technical Skills", score: 78, icon: Target, trend: "up" },
  { label: "Problem Solving", score: 88, icon: Sparkles, trend: "up" },
  { label: "Time Management", score: 76, icon: Clock, trend: "down" },
];

const questionFeedback = [
  {
    question: "Tell me about yourself and your background.",
    score: 88,
    strengths: ["Clear structure", "Relevant experience highlighted", "Confident delivery"],
    improvements: ["Could be more concise", "Add more specific achievements"],
    transcript: "I'm a software engineer with 5 years of experience in full-stack development...",
  },
  {
    question: "What are your greatest strengths and weaknesses?",
    score: 75,
    strengths: ["Honest self-assessment", "Good examples provided"],
    improvements: ["Weakness could be framed more positively", "Missing growth mindset"],
    transcript: "My greatest strength is problem-solving. I enjoy breaking down complex issues...",
  },
  {
    question: "Describe a challenging project you worked on.",
    score: 90,
    strengths: ["Used STAR method effectively", "Quantified results", "Clear action steps"],
    improvements: ["Could elaborate on team collaboration"],
    transcript: "At my previous company, we faced a critical performance issue that was affecting...",
  },
  {
    question: "Where do you see yourself in 5 years?",
    score: 80,
    strengths: ["Realistic goals", "Aligned with company growth"],
    improvements: ["Be more specific about skill development", "Mention leadership aspirations"],
    transcript: "In five years, I see myself as a senior engineer leading critical projects...",
  },
  {
    question: "Why do you want to work at this company?",
    score: 77,
    strengths: ["Research about company evident", "Passion demonstrated"],
    improvements: ["Connect personal values more strongly", "Mention specific products/teams"],
    transcript: "I've been following your company's innovations in AI for several years...",
  },
];

export default function FeedbackPage() {
  const [selectedQuestion, setSelectedQuestion] = useState(0);

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
          <p className="text-muted-foreground text-lg">Great job! Here's how you did.</p>
        </div>

        {/* Overall Score Card */}
        <Card className="bg-gradient-to-br from-primary/10 to-purple-600/10 border-primary/20 mb-8">
          <CardContent className="p-8">
            <div className="flex flex-col md:flex-row items-center justify-between gap-8">
              <div className="flex-1 text-center md:text-left">
                <h2 className="text-2xl font-bold mb-2">Overall Score</h2>
                <p className="text-muted-foreground mb-4">
                  Based on {questionFeedback.length} questions analyzed
                </p>
                <div className="flex items-center gap-4 justify-center md:justify-start">
                  <div className={`text-6xl font-bold ${getScoreColor(overallScore)}`}>
                    {overallScore}
                  </div>
                  <div className="text-left">
                    <div className="text-2xl font-bold text-muted-foreground">/100</div>
                    <Badge className="bg-green-500/20 text-green-500 border-green-500/30">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      Strong Performance
                    </Badge>
                  </div>
                </div>
              </div>
              <div className="flex-1 w-full">
                <div className="grid grid-cols-2 gap-4">
                  {metrics.map((metric, index) => (
                    <div key={index} className="bg-background/50 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <metric.icon className="h-4 w-4 text-primary" />
                        <span className="text-sm font-medium">{metric.label}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        <span className={`text-2xl font-bold ${getScoreColor(metric.score)}`}>
                          {metric.score}
                        </span>
                        {metric.trend === "up" ? (
                          <TrendingUp className="h-4 w-4 text-green-500" />
                        ) : (
                          <TrendingDown className="h-4 w-4 text-yellow-500" />
                        )}
                      </div>
                      <Progress value={metric.score} className="h-1.5 mt-2" />
                    </div>
                  ))}
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
                  {questionFeedback.map((item, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedQuestion(index)}
                      className={`w-full text-left p-4 transition-colors border-l-2 ${
                        selectedQuestion === index
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
            <Card className="bg-card/50 border-border/40">
              <CardHeader>
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="secondary">Question {selectedQuestion + 1}</Badge>
                      <Badge className={getScoreBgColor(questionFeedback[selectedQuestion].score)}>
                        Score: {questionFeedback[selectedQuestion].score}/100
                      </Badge>
                    </div>
                    <CardTitle className="text-xl">
                      {questionFeedback[selectedQuestion].question}
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
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <CheckCircle2 className="h-5 w-5 text-green-500" />
                        <h3 className="font-semibold">Strengths</h3>
                      </div>
                      <div className="space-y-2">
                        {questionFeedback[selectedQuestion].strengths.map((strength, idx) => (
                          <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
                            <CheckCircle2 className="h-4 w-4 text-green-500 mt-0.5 flex-shrink-0" />
                            <p className="text-sm">{strength}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Areas for Improvement */}
                    <div>
                      <div className="flex items-center gap-2 mb-3">
                        <AlertCircle className="h-5 w-5 text-yellow-500" />
                        <h3 className="font-semibold">Areas for Improvement</h3>
                      </div>
                      <div className="space-y-2">
                        {questionFeedback[selectedQuestion].improvements.map((improvement, idx) => (
                          <div key={idx} className="flex items-start gap-3 p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20">
                            <AlertCircle className="h-4 w-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                            <p className="text-sm">{improvement}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  </TabsContent>
                  <TabsContent value="transcript" className="mt-6">
                    <div className="bg-muted/30 rounded-lg p-6">
                      <p className="text-sm leading-relaxed">
                        {questionFeedback[selectedQuestion].transcript}
                      </p>
                    </div>
                  </TabsContent>
                </Tabs>
              </CardContent>
            </Card>

            {/* AI Recommendations */}
            <Card className="bg-gradient-to-br from-primary/5 to-purple-600/5 border-primary/20">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-primary" />
                  AI Recommendations
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-primary">1</span>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">Practice the STAR Method</h4>
                    <p className="text-sm text-muted-foreground">
                      Structure your answers using Situation, Task, Action, Result for behavioral questions.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-primary">2</span>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">Be More Specific</h4>
                    <p className="text-sm text-muted-foreground">
                      Include concrete numbers and metrics when discussing achievements and impact.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="h-6 w-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs font-bold text-primary">3</span>
                  </div>
                  <div>
                    <h4 className="font-semibold mb-1">Research the Company</h4>
                    <p className="text-sm text-muted-foreground">
                      Demonstrate deeper knowledge of the company's products, culture, and recent news.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

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