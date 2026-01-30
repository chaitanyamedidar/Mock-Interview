"use client";

import { useState, useEffect, useRef } from "react";
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

interface TranscriptMessage {
  speaker: 'user' | 'interviewer';
  text: string;
  timestamp: Date;
  isFinal?: boolean;
}

export default function InterviewPage() {
  const router = useRouter();
  const interview = useInterview();
  const [messages, setMessages] = useState<TranscriptMessage[]>([]);
  const [elapsedTime, setElapsedTime] = useState(0);
  // Removed separate state for currentResponse to avoid sync issues
  // const [currentResponse, setCurrentResponse] = useState("");
  const [sessionId, setSessionId] = useState<string>("");
  const [isAnalyzingResults, setIsAnalyzingResults] = useState(false);
  const [analysisResults, setAnalysisResults] = useState<any>(null);
  const transcriptEndRef = useRef<HTMLDivElement>(null);

  // Derive current response from messages
  const currentResponse = messages
    .filter(msg => msg.speaker === 'user')
    .map(msg => msg.text)
    .join(' ');

  // Auto-scroll to latest message
  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // VAPI Integration
  const vapi = useVAPI({
    assistantId: interview.session?.assistant_id,
    assistantConfig: interview.session?.vapi_config,
    onMessage: (message) => {
      if (message.type === 'transcript' && message.transcript) {
        const isUser = message.role === 'user';
        const transcriptType = message.transcriptType || 'final'; // Default to final if not specified
        const isFinal = transcriptType === 'final';

        setMessages(prev => {
          const lastMsg = prev[prev.length - 1];
          const isSameSpeaker = lastMsg?.speaker === (isUser ? 'user' : 'interviewer');
          
          // If we have a previous message from the same speaker that IS NOT final,
          // we should update it regardless of whether the new piece is partial or final.
          if (isSameSpeaker && !lastMsg.isFinal) {
            const updated = [...prev];
            updated[updated.length - 1] = {
              ...lastMsg,
              text: message.transcript, // Replace with new accumulated transcript
              isFinal: isFinal
            };
            return updated;
          }

          // If the last message was final, or different speaker, append new message
          return [
            ...prev,
            {
              speaker: isUser ? 'user' : 'interviewer',
              text: message.transcript,
              timestamp: new Date(),
              isFinal: isFinal
            }
          ];
        });
      }
    },
    onCallStart: () => {
      setMessages([]);
    },
    onCallEnd: async () => {
      // Call ended - Proceed to Round 2 (Technical)
      console.log('📞 Call ended, proceeding to Technical Round...');

      // Delay slightly to let the user see the visual cue of call ending
      setTimeout(() => {
        if (sessionId) {
          router.push(`/technical-interview?session_id=${sessionId}`);
        } else {
          router.push("/technical-interview");
        }
      }, 1500);
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

  const handleStartInterview = async () => {
    try {
      const result = await interview.startInterview({
        interview_type: InterviewType.BEHAVIORAL,
        difficulty: DifficultyLevel.INTERMEDIATE,
        duration: 30,
        company: "Tech Company"
      });

      // Use session_id from backend response
      const backendSessionId = result.session_id;
      setSessionId(backendSessionId);
      console.log('🆔 Using backend session ID:', backendSessionId);

      // Start VAPI call with metadata
      await vapi.start({ session_id: backendSessionId });
    } catch (error) {
      console.error("Failed to start interview:", error);
    }
  };

  // Polling function
  const pollForResults = async (sessionId: string, maxAttempts = 15): Promise<any> => {
    for (let attempt = 0; attempt < maxAttempts; attempt++) {
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/interview/results/${sessionId}`
        );

        if (response.status === 200) {
          const data = await response.json();
          return data;
        } else if (response.status === 404) {
             console.log(`Report not found yet (attempt ${attempt + 1}/${maxAttempts})`);
        } else {
             console.log(`Backend returned status ${response.status}`);
        }
      } catch (error) {
         console.error('Error polling for results:', error);
      }
      // Wait 2 seconds before retry
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
    throw new Error('Timeout waiting for interview results');
  };

  const handleToggleRecording = () => {
    if (vapi.isCallActive) {
      vapi.stop();
    } else {
      vapi.start();
    }
  };

  const handleNextQuestion = async () => {
    interview.nextQuestion();
    setMessages([]);
  };

  const handleEndInterview = async () => {
    try {
      // Stop VAPI call if active
      if (vapi.isCallActive) {
        await vapi.stop();
      }

      // Format transcript for backend
      const formattedTranscript = messages.map(msg => ({
        role: msg.speaker === 'user' ? 'user' : 'assistant',
        message: msg.text,
        timestamp: msg.timestamp.toISOString()
      }));

      console.log('📝 Sending transcript for analysis:', formattedTranscript.length, 'messages');

      await interview.endInterview(formattedTranscript);
      // Navigate to Round 2 (Technical Interview)
      router.push(`/technical-interview?session_id=${sessionId}`);
    } catch (error) {
      console.error("Failed to end interview:", error);
      // Navigate to technical round even if there's an error
      router.push(`/technical-interview?session_id=${sessionId}`);
    }
  };

  const handleEndInterviewWithConfirmation = () => {
    if (window.confirm("Are you sure you want to end Round 1? You will proceed to Round 2 (Technical Interview).")) {
      handleEndInterview();
    }
  };

  const handleSkipToTechnical = () => {
    if (window.confirm("Skip Round 1 and go directly to the Technical Interview? You will not receive behavioral feedback.")) {
      router.push(`/technical-interview${sessionId ? `?session_id=${sessionId}` : ''}`);
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
                <AlertDescription>
                  {typeof interview.error === 'string'
                    ? interview.error
                    : typeof interview.error === 'object'
                      ? JSON.stringify(interview.error)
                      : String(interview.error)
                  }
                </AlertDescription>
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
            <div className="flex flex-col gap-4 pt-4">
              <Button
                size="lg"
                className="w-full bg-primary hover:bg-primary/90"
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
                    Start Round 1 - Behavioral
                  </>
                )}
              </Button>
              <div className="flex gap-4">
                <Button
                  size="lg"
                  variant="outline"
                  className="flex-1"
                  onClick={handleSkipToTechnical}
                >
                  <SkipForward className="mr-2 h-5 w-5" />
                  Skip to Round 2
                </Button>
                <Link href="/" className="flex-1">
                  <Button size="lg" variant="outline" className="w-full">
                    Go Back
                  </Button>
                </Link>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-background via-background to-background/95">
      {/* Header */}
      <header className="w-full border-b border-border/40 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <Sparkles className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-bold">InterviewAI</span>
            </div>
            <Badge variant="secondary" className="text-sm px-4 py-2">
              Round {Math.floor(interview.currentQuestionIndex / 2) + 1}
            </Badge>
          </div>
        </div>
      </header>

      <div className="w-full min-h-[calc(100vh-64px)] px-6 py-4 bg-background flex flex-col">
        <div className="max-w-7xl mx-auto w-full flex-1 flex flex-col">
          {interview.error && (
            <Alert variant="destructive" className="mb-4">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>
                {typeof interview.error === 'string'
                  ? interview.error
                  : typeof interview.error === 'object'
                    ? JSON.stringify(interview.error)
                    : String(interview.error)
                }
              </AlertDescription>
            </Alert>
          )}
          <div className="grid lg:grid-cols-2 gap-6 flex-1">
            {/* Left Column - Voice Visualizer & Controls */}
            <div className="space-y-6">
              {/* Question Card */}
              <Card className="bg-card/50 border-border/40">
                <CardContent className="p-6">
                  <div className="flex items-start gap-3 mb-4">
                    <Volume2 className="h-5 w-5 text-primary mt-1 flex-shrink-0" />
                    <div>
                      <h3 className="font-semibold mb-1">
                        Round {Math.floor(interview.currentQuestionIndex / 2) + 1} - {interview.currentQuestionIndex % 2 === 0 ? 'Behavioral' : 'Technical'}
                      </h3>
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
                        className={`h-40 w-40 rounded-full flex items-center justify-center transition-all duration-300 ${vapi.isCallActive
                          ? "bg-primary/20 shadow-lg shadow-primary/50"
                          : "bg-muted/50"
                          }`}
                        style={{
                          transform: vapi.isCallActive ? "scale(1.05)" : "scale(1)",
                        }}
                      >
                        <div
                          className={`h-32 w-32 rounded-full flex items-center justify-center transition-all duration-200 ${vapi.isCallActive
                            ? "bg-primary/30"
                            : "bg-muted"
                            }`}
                        >
                          <div
                            className={`h-24 w-24 rounded-full flex items-center justify-center ${vapi.isCallActive
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
                          className={`w-2 rounded-full transition-all duration-100 ${vapi.isCallActive ? "bg-primary" : "bg-muted"
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
                    {messages.filter(msg => msg.speaker === 'interviewer').length === 0 ? (
                      <div className="text-center py-8 text-muted-foreground text-sm">
                        Interviewer responses will appear here...
                      </div>
                    ) : (
                      messages.filter(msg => msg.speaker === 'interviewer').map((msg, idx) => (
                        <div
                          key={idx}
                          className="flex gap-3 p-3 rounded-lg bg-muted/50"
                        >
                          <div className="flex-shrink-0">
                            <div className="h-8 w-8 rounded-full flex items-center justify-center bg-purple-500/20 text-purple-500">
                              <span className="text-xs font-bold">AI</span>
                            </div>
                          </div>
                          <div className="flex-1 min-w-0">
                            <div className="flex items-baseline gap-2 mb-1">
                              <span className="text-xs font-medium text-muted-foreground">
                                Interviewer
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
                    <div ref={transcriptEndRef} />
                  </div>
                </CardContent>
              </Card>

              {/* VAPI Error (if any) */}
              {vapi.error && (
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>
                    {typeof vapi.error === 'string'
                      ? vapi.error
                      : typeof vapi.error === 'object'
                        ? JSON.stringify(vapi.error)
                        : String(vapi.error)
                    }
                  </AlertDescription>
                </Alert>
              )}

              {/* Your Response */}
              <Card className="bg-card/50 border-border/40">
                <CardContent className="p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <MessageSquare className="h-5 w-5 text-primary" />
                    <h3 className="font-semibold">Your Response</h3>
                  </div>
                  <div className="min-h-[100px] p-4 rounded-lg bg-muted/30 max-h-60 overflow-y-auto">
                    {currentResponse ? (
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{currentResponse}</p>
                    ) : (
                      <p className="text-sm text-muted-foreground italic">
                        Start speaking to see your response here...
                      </p>
                    )}
                  </div>
                </CardContent>
              </Card>

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

          {/* End Interview Button at Bottom */}
          <div className="w-full max-w-7xl mx-auto mt-6 pb-4">
            <Button
              size="lg"
              variant="destructive"
              className="w-full bg-red-600 hover:bg-red-700 text-white font-semibold py-6"
              onClick={handleEndInterviewWithConfirmation}
              disabled={interview.isLoading}
            >
              {interview.isLoading ? (
                <>
                  <Loader2 className="mr-2 h-5 w-5 animate-spin" />
                  Ending Interview...
                </>
              ) : (
                <>
                  <StopCircle className="mr-2 h-6 w-6" />
                  End Interview
                </>
              )}
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}