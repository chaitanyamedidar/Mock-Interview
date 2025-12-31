"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { 
  Mic, 
  MicOff, 
  SkipForward, 
  StopCircle, 
  Play,
  Clock,
  MessageSquare,
  Volume2,
  Sparkles,
  AlertCircle,
  Loader2
} from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useInterview } from "@/hooks/useInterview";
import { InterviewType, DifficultyLevel } from "@/lib/api";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useVAPI } from "@/hooks/useVAPI";
import FeedbackDisplay from "@/components/FeedbackDisplay";

interface TranscriptMessage {
  speaker: 'user' | 'interviewer';
  text: string;
  timestamp: Date;
}

export default function InterviewPage() {
  const router = useRouter();
  const interview = useInterview();
  const [messages, setMessages] = useState<TranscriptMessage[]>([]);
  const [elapsedTime, setElapsedTime] = useState(0);
  const [currentResponse, setCurrentResponse] = useState("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [currentFeedback, setCurrentFeedback] = useState<any>(null);

  // VAPI Integration
  const vapi = useVAPI({
    onMessage: (message) => {
      if (message.type === 'transcript' && message.transcript) {
        const isUser = message.role === 'user';
        setMessages(prev => [
          ...prev,
          {
            speaker: isUser ? 'user' : 'interviewer',
            text: message.transcript,
            timestamp: new Date()
          }
        ]);
        if (isUser) {
          setCurrentResponse(prev => prev + ' ' + message.transcript);
        }
      }
    },
    onCallStart: () => {
      setMessages([]);
      setCurrentResponse('');
    },
    onCallEnd: () => {
      if (currentResponse.trim()) {
        handleAnalyzeResponse();
      }
    },
    onError: (error) => {
      console.error('VAPI error:', error);
    }
  });

  // Timer effect
  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (interview.isStarted) {
      interval = setInterval(() => {
        setElapsedTime((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [interview.isStarted]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  // Analyze response with ML model
  const handleAnalyzeResponse = async () => {
    if (!currentResponse.trim()) return;
    
    setIsAnalyzing(true);
    try {
      const response = await fetch('/api/interview/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: interview.session?.session_id,
          response_text: currentResponse,
          interview_type: 'behavioral'
        })
      });

      if (response.ok) {
        const feedback = await response.json();
        console.log('Received feedback:', feedback);
        setCurrentFeedback(feedback);
        // Move to next question after analysis
        setTimeout(() => {
          interview.nextQuestion();
          setTranscript("");
          setCurrentResponse("");
          setCurrentFeedback(null);
        }, 5000); // Show feedback for 5 seconds
      }
    } catch (error) {
      console.error('Error analyzing response:', error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleStartInterview = async () => {
    try {
      await interview.startInterview({
        interview_type: InterviewType.BEHAVIORAL,
        difficulty: DifficultyLevel.INTERMEDIATE,
        duration: 30,
        company: "Tech Company"
      });
      // Start VAPI call
      await vapi.start();
    } catch (error) {
      console.error("Failed to start interview:", error);
    }
  };

  const handleToggleRecording = () => {
    if (vapi.isCallActive) {
      vapi.stop();
    } else {
      vapi.start();
    }
  };

  const handleNextQuestion = async () => {
    if (currentResponse.trim()) {
      try {
        await interview.analyzeResponse(currentResponse);
        interview.nextQuestion();
        setMessages([]);
        setCurrentResponse("");
      } catch (error) {
        console.error("Failed to analyze response:", error);
      }
    } else {
      interview.nextQuestion();
      setMessages([]);
      setCurrentResponse("");
    }
  };

  const handleEndInterview = async () => {
    try {
      if (currentResponse.trim()) {
        await interview.analyzeResponse(currentResponse);
      }
      await interview.endInterview();
      router.push("/feedback");
    } catch (error) {
      console.error("Failed to end interview:", error);
      router.push("/feedback");
    }
  };

  const currentQuestion = interview.getCurrentQuestion();
  const progress = interview.getProgress();

  if (!interview.isStarted) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full bg-card/50 border-border/40">
          <CardContent className="p-12 text-center space-y-6">
            <div className="h-20 w-20 mx-auto rounded-full bg-primary/10 flex items-center justify-center">
              <Mic className="h-10 w-10 text-primary" />
            </div>
            <h1 className="text-3xl font-bold">Ready to Start Your Interview?</h1>
            <p className="text-muted-foreground text-lg">
              This behavioral interview will test your communication and experience. Take your time and answer naturally.
            </p>
            {interview.error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{interview.error}</AlertDescription>
              </Alert>
            )}
            <div className="grid grid-cols-2 gap-4 pt-4">
              <div className="p-4 rounded-lg bg-muted/50">
                <Clock className="h-6 w-6 text-primary mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Duration</p>
                <p className="font-semibold">~30 min</p>
              </div>
              <div className="p-4 rounded-lg bg-muted/50">
                <MessageSquare className="h-6 w-6 text-primary mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">Type</p>
                <p className="font-semibold">Behavioral</p>
              </div>
            </div>
            <div className="flex flex-col sm:flex-row gap-4 pt-4">
              <Button 
                size="lg" 
                className="flex-1 bg-primary hover:bg-primary/90"
                onClick={handleStartInterview}
                disabled={interview.isLoading}
              >
                {interview.isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                    Starting...
                  </>
                ) : (
                  <>
                    <Play className="mr-2 h-5 w-5" />
                    Start Interview
                  </>
                )}
              </Button>
              <Link href="/" className="flex-1">
                <Button size="lg" variant="outline" className="w-full">
                  Go Back
                </Button>
              </Link>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header with Progress */}
      <header className="border-b border-border/40 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-bold">InterviewAI</span>
            </div>
            <div className="flex items-center gap-4">
              <Badge variant="secondary" className="text-sm">
                <Clock className="h-3 w-3 mr-1" />
                {formatTime(elapsedTime)}
              </Badge>
              <Badge variant="secondary" className="text-sm">
                Question {interview.currentQuestionIndex + 1}/{interview.questions.length}
              </Badge>
            </div>
          </div>
          <Progress value={progress} className="h-1" />
        </div>
      </header>

      <div className="container mx-auto px-4 py-8 max-w-6xl">
        {interview.error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{interview.error}</AlertDescription>
          </Alert>
        )}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Left Column - Voice Visualizer & Controls */}
          <div className="space-y-6">
            {/* Question Card */}
            <Card className="bg-card/50 border-border/40">
              <CardContent className="p-6">
                <div className="flex items-start gap-3 mb-4">
                  <Volume2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                  <div>
                    <h3 className="font-semibold mb-1">Question {interview.currentQuestionIndex + 1}</h3>
                    <p className="text-lg text-foreground leading-relaxed">
                      {currentQuestion?.question_text || "Loading question..."}
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Voice Visualizer */}
            <Card className="bg-card/50 border-border/40">
              <CardContent className="p-8">
                <div className="flex flex-col items-center justify-center space-y-8">
                  {/* Circular Voice Indicator */}
                  <div className="relative">
                    <div 
                      className={`h-40 w-40 rounded-full flex items-center justify-center transition-all duration-300 ${
                        vapi.isCallActive 
                          ? "bg-primary/20 shadow-lg shadow-primary/50" 
                          : "bg-muted/50"
                      }`}
                      style={{
                        transform: vapi.isCallActive ? "scale(1.05)" : "scale(1)",
                      }}
                    >
                      <div 
                        className={`h-32 w-32 rounded-full flex items-center justify-center transition-all duration-200 ${
                          vapi.isCallActive 
                            ? "bg-primary/30" 
                            : "bg-muted"
                        }`}
                      >
                        <div 
                          className={`h-24 w-24 rounded-full flex items-center justify-center ${
                            vapi.isCallActive 
                              ? "bg-primary" 
                              : "bg-muted-foreground/20"
                          }`}
                        >
                          {vapi.isCallActive ? (
                            <Mic className="h-12 w-12 text-primary-foreground" />
                          ) : (
                            <MicOff className="h-12 w-12 text-muted-foreground" />
                          )}
                        </div>
                      </div>
                    </div>
                    {vapi.isCallActive && (
                      <div className="absolute -inset-4 rounded-full border-2 border-primary/30 animate-ping" />
                    )}
                  </div>

                  {/* Status */}
                  <div className="text-center">
                    <p className={`text-sm font-medium ${vapi.isCallActive ? "text-primary" : "text-muted-foreground"}`}>
                      {vapi.isCallActive ? (vapi.isSpeaking ? "AI Speaking..." : "Listening...") : "Paused"}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {vapi.isCallActive ? "Speak naturally and clearly" : "Click the mic button to start"}
                    </p>
                    {vapi.error && (
                      <p className="text-xs text-destructive mt-1">{vapi.error}</p>
                    )}
                  </div>

                  {/* Audio Level Bars */}
                  <div className="flex gap-1 h-12 items-end justify-center w-full">
                    {[...Array(20)].map((_, i) => (
                      <div
                        key={i}
                        className={`w-2 rounded-full transition-all duration-100 ${
                          vapi.isCallActive ? "bg-primary" : "bg-muted"
                        }`}
                        style={{
                          height: vapi.isCallActive && vapi.isSpeaking
                            ? `${Math.max(20, Math.random() * 80)}%` 
                            : "20%",
                        }}
                      />
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Control Buttons */}
            <div className="flex gap-3">
              <Button
                size="lg"
                variant={vapi.isCallActive ? "destructive" : "default"}
                className="flex-1"
                onClick={handleToggleRecording}
                disabled={vapi.error !== null}
              >
                {vapi.isCallActive ? (
                  <>
                    <MicOff className="mr-2 h-5 w-5" />
                    Stop Call
                  </>
                ) : (
                  <>
                    <Mic className="mr-2 h-5 w-5" />
                    Start Call
                  </>
                )}
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={handleNextQuestion}
                disabled={interview.isLastQuestion() || interview.isLoading}
              >
                {interview.isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <SkipForward className="h-5 w-5" />
                )}
              </Button>
              <Button
                size="lg"
                variant="outline"
                onClick={handleEndInterview}
                disabled={interview.isLoading}
              >
                {interview.isLoading ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <StopCircle className="h-5 w-5" />
                )}
              </Button>
            </div>
          </div>

          {/* Right Column - Transcript & Feedback */}
          <div className="space-y-6">
            {/* Realtime Transcript */}
            <Card className="bg-card/50 border-border/40">
              <CardContent className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <MessageSquare className="h-5 w-5 text-primary" />
                  <h3 className="font-semibold">Conversation Transcript</h3>
                </div>
                <div className="space-y-3 max-h-96 overflow-y-auto">
                  {messages.length === 0 ? (
                    <div className="text-center py-8 text-muted-foreground text-sm">
                      Start speaking to see the transcript...
                    </div>
                  ) : (
                    messages.map((msg, idx) => (
                      <div 
                        key={idx}
                        className={`flex gap-3 p-3 rounded-lg ${
                          msg.speaker === 'user' 
                            ? 'bg-primary/10 ml-4' 
                            : 'bg-muted/50 mr-4'
                        }`}
                      >
                        <div className="flex-shrink-0">
                          <div className={`h-8 w-8 rounded-full flex items-center justify-center ${
                            msg.speaker === 'user'
                              ? 'bg-primary/20 text-primary'
                              : 'bg-purple-500/20 text-purple-500'
                          }`}>
                            {msg.speaker === 'user' ? (
                              <span className="text-xs font-bold">YOU</span>
                            ) : (
                              <span className="text-xs font-bold">AI</span>
                            )}
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-baseline gap-2 mb-1">
                            <span className="text-xs font-medium text-muted-foreground">
                              {msg.speaker === 'user' ? 'You' : 'Interviewer'}
                            </span>
                            <span className="text-xs text-muted-foreground/60">
                              {msg.timestamp.toLocaleTimeString()}
                            </span>
                          </div>
                          <p className="text-sm leading-relaxed break-words">
                            {msg.text}
                          </p>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
            
            {/* VAPI Error (if any) */}
            {vapi.error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{vapi.error}</AlertDescription>
              </Alert>
            )}
            
            <FeedbackDisplay 
              feedback={currentFeedback}
              transcript={currentResponse}
              isAnalyzing={isAnalyzing}
            />

            {/* Tips Card */}
            <Card className="bg-gradient-to-br from-primary/10 to-purple-600/10 border-primary/20">
              <CardContent className="p-6">
                <h4 className="font-semibold mb-3 flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-primary" />
                  Interview Tip
                </h4>
                <p className="text-sm text-muted-foreground">
                  Use the STAR method: Situation, Task, Action, Result. Structure your answer to provide clear, concise examples.
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}