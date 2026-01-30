"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import Editor from "@monaco-editor/react";
import {
  Code2,
  Lightbulb,
  AlertCircle,
  Loader2,
  StopCircle,
  Sparkles,
  Copy,
  CheckCircle2,
  Mic,
  MicOff,
} from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useVAPI } from "@/hooks/useVAPI";
import { apiService } from "@/lib/api";

interface CodeSnapshot {
  code: string;
  timestamp: Date;
  lineCount: number;
}

export default function TechnicalInterviewPage() {
  const router = useRouter();
  const [code, setCode] = useState("// Start coding here...\n\n");
  const [language, setLanguage] = useState("javascript");
  const [snapshots, setSnapshots] = useState<CodeSnapshot[]>([]);
  const [suspiciousActivity, setSuspiciousActivity] = useState<string[]>([]);
  const [lastTypingTime, setLastTypingTime] = useState<number>(Date.now());
  const [showHint, setShowHint] = useState(false);
  const [voiceHelpActive, setVoiceHelpActive] = useState(false);
  const [voiceHelpDuration, setVoiceHelpDuration] = useState(0);
  const [question, setQuestion] = useState<any>(null);
  const [isLoadingQuestion, setIsLoadingQuestion] = useState(true);
  const [questionError, setQuestionError] = useState<string | null>(null);
  const searchParams = useSearchParams();
  const snapshotIntervalRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const inactivityTimerRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const maxDurationTimerRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const reminderIntervalRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const durationIntervalRef = useRef<NodeJS.Timeout | undefined>(undefined);


  // VAPI Integration
  const vapi = useVAPI({
    onMessage: (message) => {
      // Reset inactivity timer on any VAPI message
      resetInactivityTimer();

      // Handle VAPI messages
      if (message.type === "function-call" && message.functionCall?.name === "requestHint") {
        setShowHint(true);
      }
    },
    onCallStart: () => {
      console.log("Voice help started");
      setVoiceHelpActive(true);
      setVoiceHelpDuration(0);
      startVoiceHelpTimers();
    },
    onCallEnd: () => {
      console.log("Voice help ended");
      setVoiceHelpActive(false);
      stopVoiceHelpTimers();
    },
    onSpeechStart: () => {
      // Reset inactivity timer when user starts speaking
      resetInactivityTimer();
    },
  });

  // Fetch question on mount
  useEffect(() => {
    const fetchQuestion = async () => {
      try {
        setIsLoadingQuestion(true);
        setQuestionError(null);

        // Get company from URL params if available
        const company = searchParams?.get('company') || undefined;
        const difficulty = searchParams?.get('difficulty') || undefined;

        const fetchedQuestion = await apiService.getRandomCodingQuestion({
          company,
          difficulty
        });

        setQuestion(fetchedQuestion);
      } catch (error) {
        console.error('Failed to fetch question:', error);
        setQuestionError('Failed to load question. Please try again.');
        // Fallback to hardcoded question
        setQuestion({
          title: "Two Sum",
          difficulty: "Easy",
          description: "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
          examples: [
            { input: "nums = [2,7,11,15], target = 9", output: "[0,1]", explanation: "Because nums[0] + nums[1] == 9, we return [0, 1]." }
          ],
          constraints: ["2 <= nums.length <= 10^4"],
          hints: ["Use a hash map to store numbers you've already seen."],
        });
      } finally {
        setIsLoadingQuestion(false);
      }
    };

    fetchQuestion();
  }, [searchParams]);

  // Start voice help timers
  const startVoiceHelpTimers = () => {
    // Reset inactivity timer (90 seconds)
    resetInactivityTimer();

    // Max duration timer (5 minutes)
    maxDurationTimerRef.current = setTimeout(() => {
      console.log("Max voice help duration reached (5 minutes)");
      endVoiceHelp();
    }, 5 * 60 * 1000);

    // Periodic reminders (every 1 minute)
    reminderIntervalRef.current = setInterval(() => {
      console.log("Voice help reminder: Still active");
      // Optionally send a subtle reminder to VAPI
    }, 60 * 1000);

    // Duration counter (update every second)
    durationIntervalRef.current = setInterval(() => {
      setVoiceHelpDuration(prev => prev + 1);
    }, 1000);
  };

  // Reset inactivity timer
  const resetInactivityTimer = () => {
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }

    inactivityTimerRef.current = setTimeout(() => {
      console.log("Voice help inactivity timeout (90 seconds)");
      endVoiceHelp();
    }, 90 * 1000);
  };

  // Stop all voice help timers
  const stopVoiceHelpTimers = () => {
    if (inactivityTimerRef.current) {
      clearTimeout(inactivityTimerRef.current);
    }
    if (maxDurationTimerRef.current) {
      clearTimeout(maxDurationTimerRef.current);
    }
    if (reminderIntervalRef.current) {
      clearInterval(reminderIntervalRef.current);
    }
    if (durationIntervalRef.current) {
      clearInterval(durationIntervalRef.current);
    }
  };

  // Start code monitoring (snapshots every 15 seconds)
  const startCodeMonitoring = () => {
    snapshotIntervalRef.current = setInterval(() => {
      captureCodeSnapshot();
    }, 15000);
  };

  // Stop code monitoring
  const stopCodeMonitoring = () => {
    if (snapshotIntervalRef.current) {
      clearInterval(snapshotIntervalRef.current);
    }
  };

  // Capture code snapshot
  const captureCodeSnapshot = () => {
    const snapshot: CodeSnapshot = {
      code,
      timestamp: new Date(),
      lineCount: code.split("\n").length,
    };
    setSnapshots((prev) => [...prev, snapshot]);

    // Only send to VAPI if voice help is active
    if (voiceHelpActive && vapi.send) {
      vapi.send({
        type: "add-message",
        message: {
          role: "system",
          content: `Code snapshot at ${snapshot.timestamp.toLocaleTimeString()}:\n\`\`\`${language}\n${code}\n\`\`\`\nLines: ${snapshot.lineCount}`,
        },
      } as any);
    }

    console.log("Code snapshot captured:", snapshot);
  };

  // Handle code change
  const handleCodeChange = (value: string | undefined) => {
    if (!value) return;

    const now = Date.now();
    const timeSinceLastType = now - lastTypingTime;

    // Detect suspiciously fast typing (more than 100 chars in less than 1 second)
    if (value.length - code.length > 100 && timeSinceLastType < 1000) {
      const alert = `Fast typing detected: ${value.length - code.length} characters in ${timeSinceLastType}ms`;
      setSuspiciousActivity((prev) => [...prev, alert]);
      console.warn(alert);
    }

    setCode(value);
    setLastTypingTime(now);
  };

  // Handle paste event
  const handleEditorPaste = (e: any) => {
    const pastedText = e.clipboardData?.getData("text") || "";

    if (pastedText.length > 100) {
      const alert = `Large paste detected: ${pastedText.length} characters`;
      setSuspiciousActivity((prev) => [...prev, alert]);
      console.warn(alert);

      // Optionally show warning to user
      if (window.confirm("Large code paste detected. Are you sure you want to paste this code? This activity is being monitored.")) {
        return true;
      } else {
        e.preventDefault();
        return false;
      }
    }
  };

  // Request hint from VAPI
  const requestHint = () => {
    setShowHint(true);

    // Send request to VAPI if voice help is active
    if (voiceHelpActive && vapi.send) {
      vapi.send({
        type: "add-message",
        message: {
          role: "user",
          content: `I need a hint for the problem. Here's my current code:\n\`\`\`${language}\n${code}\n\`\`\``,
        },
      } as any);
    }
  };

  // Toggle voice help
  const toggleVoiceHelp = () => {
    if (voiceHelpActive) {
      endVoiceHelp();
    } else {
      startVoiceHelp();
    }
  };

  // Start voice help
  const startVoiceHelp = () => {
    vapi.start();
  };

  // End voice help
  const endVoiceHelp = () => {
    if (vapi.isCallActive) {
      vapi.stop();
    }
  };

  // Format duration as MM:SS
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // End interview with confirmation
  const handleEndInterview = () => {
    if (window.confirm("Are you sure you want to end the technical interview? Your code will be submitted for review.")) {
      stopCodeMonitoring();
      stopVoiceHelpTimers();
      if (vapi.isCallActive) {
        vapi.stop();
      }
      // Submit code and navigate to feedback
      submitCode();
    }
  };

  // Submit code for evaluation
  const submitCode = async () => {
    try {
      const sessionId = searchParams?.get('session_id') || "mock-session-id";

      const response = await fetch("/api/technical/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: sessionId,
          code,
          language,
          snapshots,
          suspiciousActivity,
          question: question ? question.title : "Unknown",
          question_description: question ? question.description : "",
        }),
      });

      if (response.ok) {
        // Ensure we pass the session_id to the feedback page
        router.push(`/feedback?session_id=${sessionId}`);
      } else {
        console.error("Failed to submit code, response not ok");
        // Still redirect to feedback to show whatever data we have
        router.push(`/feedback?session_id=${sessionId}`);
      }
    } catch (error) {
      console.error("Failed to submit code:", error);
      const sessionId = searchParams?.get('session_id') || "mock-session-id";
      router.push(`/feedback?session_id=${sessionId}`);
    }
  };

  // Start code monitoring on mount
  useEffect(() => {
    startCodeMonitoring();
    return () => {
      stopCodeMonitoring();
      stopVoiceHelpTimers();
      if (vapi.isCallActive) {
        vapi.stop();
      }
    };
  }, []);

  return (
    <div className="min-h-screen w-full bg-gradient-to-br from-background via-background to-background/95">
      {/* Header */}
      <header className="w-full border-b border-border/40 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <Code2 className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-bold">InterviewAI</span>
            </div>
            <div className="flex items-center gap-3">
              <Badge variant="secondary" className="text-sm px-4 py-2">
                Round 2 - Technical
              </Badge>
              {voiceHelpActive && (
                <Badge variant="default" className="text-sm px-3 py-2 bg-green-600">
                  🎙️ Voice Help Active - {formatDuration(voiceHelpDuration)}
                </Badge>
              )}
              {suspiciousActivity.length > 0 && (
                <Badge variant="destructive" className="text-sm px-3 py-2">
                  ⚠️ {suspiciousActivity.length} Alert{suspiciousActivity.length > 1 ? "s" : ""}
                </Badge>
              )}
              <Button
                variant={voiceHelpActive ? "destructive" : "outline"}
                size="sm"
                onClick={toggleVoiceHelp}
                disabled={vapi.isLoading}
                className={voiceHelpActive ? "" : "border-primary text-primary hover:bg-primary hover:text-primary-foreground"}
              >
                {vapi.isLoading ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : voiceHelpActive ? (
                  <MicOff className="h-4 w-4 mr-2" />
                ) : (
                  <Mic className="h-4 w-4 mr-2" />
                )}
                {voiceHelpActive ? "End Voice Help" : "Request Voice Help"}
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - Split Screen */}
      <div className="w-full h-[calc(100vh-64px)] flex flex-col">
        <div className="flex-1 grid lg:grid-cols-2 gap-0">
          {/* Left Panel - Question & Hints */}
          <div className="border-r border-border/40 overflow-y-auto p-6 bg-background">
            {isLoadingQuestion ? (
              <div className="max-w-3xl mx-auto flex items-center justify-center h-full">
                <div className="text-center space-y-4">
                  <Loader2 className="h-12 w-12 animate-spin mx-auto text-primary" />
                  <p className="text-muted-foreground">Loading your coding question...</p>
                </div>
              </div>
            ) : questionError ? (
              <div className="max-w-3xl mx-auto">
                <Alert variant="destructive">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{questionError}</AlertDescription>
                </Alert>
              </div>
            ) : question ? (
              <div className="max-w-3xl mx-auto space-y-6">
                {/* Question Title */}
                <div className="flex items-center justify-between">
                  <h1 className="text-2xl font-bold">{question.title}</h1>
                  <Badge
                    variant={
                      question.difficulty === "Easy"
                        ? "default"
                        : question.difficulty === "Medium"
                          ? "secondary"
                          : "destructive"
                    }
                  >
                    {question.difficulty}
                  </Badge>
                </div>

                {/* Description */}
                <Card className="bg-card/50 border-border/40">
                  <CardContent className="p-6">
                    <h3 className="font-semibold mb-3">Description</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {question.description}
                    </p>
                  </CardContent>
                </Card>

                {/* Examples */}
                <Card className="bg-card/50 border-border/40">
                  <CardContent className="p-6">
                    <h3 className="font-semibold mb-4">Examples</h3>
                    <div className="space-y-4">
                      {question.examples.map((example, idx) => (
                        <div key={idx} className="space-y-2">
                          <div className="flex items-center gap-2">
                            <span className="font-medium">Example {idx + 1}:</span>
                          </div>
                          <div className="bg-muted/30 p-3 rounded font-mono text-sm space-y-1">
                            <div>
                              <span className="text-muted-foreground">Input:</span> {example.input}
                            </div>
                            <div>
                              <span className="text-muted-foreground">Output:</span> {example.output}
                            </div>
                            {example.explanation && (
                              <div className="text-muted-foreground text-xs pt-2">
                                {example.explanation}
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Constraints */}
                <Card className="bg-card/50 border-border/40">
                  <CardContent className="p-6">
                    <h3 className="font-semibold mb-3">Constraints</h3>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      {question.constraints.map((constraint, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <span className="text-primary mt-1">•</span>
                          <span className="font-mono">{constraint}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>

                {/* Hints Section */}
                <Card className="bg-gradient-to-br from-amber-50/50 to-orange-50/50 dark:from-amber-950/20 dark:to-orange-950/20 border-amber-200/50 dark:border-amber-800/50">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold flex items-center gap-2">
                        <Lightbulb className="h-5 w-5 text-amber-600" />
                        Hints
                      </h3>
                      {!showHint && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={requestHint}
                          className="text-amber-700 border-amber-300"
                        >
                          Request Hint
                        </Button>
                      )}
                    </div>
                    {showHint ? (
                      <div className="space-y-3">
                        {question.hints.map((hint, idx) => (
                          <div
                            key={idx}
                            className="flex items-start gap-2 text-sm text-muted-foreground"
                          >
                            <span className="text-amber-600 font-bold">{idx + 1}.</span>
                            <span>{hint}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">
                        Click "Request Hint" if you need help. You can also ask the interviewer for hints via voice.
                      </p>
                    )}
                  </CardContent>
                </Card>

                {/* VAPI Error */}
                {vapi.error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{vapi.error}</AlertDescription>
                  </Alert>
                )}
              </div>
            ) : null}
          </div>

          {/* Right Panel - Code Editor */}
          <div className="flex flex-col bg-[#1e1e1e]">
            {/* Editor Toolbar */}
            <div className="bg-[#252526] border-b border-border/20 px-4 py-2 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <select
                  value={language}
                  onChange={(e) => setLanguage(e.target.value)}
                  className="bg-[#3c3c3c] text-white px-3 py-1.5 rounded text-sm border border-border/20"
                >
                  <option value="javascript">JavaScript</option>
                  <option value="typescript">TypeScript</option>
                  <option value="python">Python</option>
                  <option value="java">Java</option>
                  <option value="cpp">C++</option>
                </select>
                <Badge variant="outline" className="text-xs">
                  {code.split("\n").length} lines
                </Badge>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => navigator.clipboard.writeText(code)}
                  className="text-white hover:bg-[#3c3c3c]"
                >
                  <Copy className="h-4 w-4 mr-1" />
                  Copy
                </Button>
              </div>
            </div>

            {/* Monaco Editor */}
            <div className="flex-1">
              <Editor
                height="100%"
                language={language}
                value={code}
                onChange={handleCodeChange}
                theme="vs-dark"
                options={{
                  minimap: { enabled: true },
                  fontSize: 14,
                  lineNumbers: "on",
                  scrollBeyondLastLine: false,
                  automaticLayout: true,
                  tabSize: 2,
                  wordWrap: "on",
                }}
                onMount={(editor) => {
                  // Add paste event listener
                  editor.onDidPaste(() => {
                    const selection = editor.getSelection();
                    if (selection) {
                      const selectedText = editor.getModel()?.getValueInRange(selection) || "";
                      if (selectedText.length > 100) {
                        handleEditorPaste({ clipboardData: { getData: () => selectedText } });
                      }
                    }
                  });
                }}
              />
            </div>
          </div>
        </div>

        {/* Bottom Action Bar */}
        <div className="w-full border-t border-border/40 bg-background/95 backdrop-blur-sm p-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Badge variant="outline" className="text-xs">
                Auto-saving code snapshots every 15s
              </Badge>
              {snapshots.length > 0 && (
                <Badge variant="secondary" className="text-xs">
                  <CheckCircle2 className="h-3 w-3 mr-1" />
                  {snapshots.length} snapshot{snapshots.length > 1 ? "s" : ""} saved
                </Badge>
              )}
            </div>
            <Button
              size="lg"
              variant="destructive"
              className="bg-red-600 hover:bg-red-700"
              onClick={handleEndInterview}
            >
              <StopCircle className="mr-2 h-5 w-5" />
              Submit & End Interview
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}
