"use client";

import { useState, useRef } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { 
  FileText, 
  Upload, 
  Sparkles, 
  CheckCircle2, 
  AlertCircle, 
  TrendingUp,
  Award,
  Target,
  Zap,
  ArrowLeft,
  Loader2,
  X
} from "lucide-react";
import Link from "next/link";

interface CategoryScores {
  formatting: number;
  keywords: number;
  structure: number;
  impact: number;
  readability: number;
}

interface CriticalIssue {
  issue: string;
  severity: "high" | "medium" | "low";
  suggestion: string;
}

interface KeywordAnalysis {
  found_keywords: string[];
  missing_keywords: string[];
  keyword_density: string;
}

interface ResumeAnalysis {
  overall_score: number;
  ats_score: number;
  rating: string;
  category_scores: CategoryScores;
  key_strengths: string[];
  critical_issues: CriticalIssue[];
  missing_sections: string[];
  keyword_analysis: KeywordAnalysis;
  formatting_issues: string[];
  recommendations: string[];
  summary: string;
}

export default function ResumePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [jobDescription, setJobDescription] = useState("");
  const [targetRole, setTargetRole] = useState("");
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      // Validate file type
      const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
      const validExtensions = ['.pdf', '.docx', '.txt'];
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      
      if (!validTypes.includes(file.type) && !validExtensions.includes(fileExtension)) {
        setError("Please upload a PDF, DOCX, or TXT file");
        return;
      }
      
      setSelectedFile(file);
      setError(null);
    }
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Please select a resume file");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (jobDescription) formData.append('job_description', jobDescription);
      if (targetRole) formData.append('target_role', targetRole);

      const response = await fetch("http://localhost:8000/api/resume/analyze", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to analyze resume");
      }

      const data = await response.json();
      setAnalysis(data);
    } catch (err: any) {
      setError(err.message || "Failed to analyze resume. Please try again.");
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getRatingColor = (rating: string) => {
    switch (rating) {
      case "Excellent":
        return "text-green-600 bg-green-50 border-green-200";
      case "Good":
        return "text-blue-600 bg-blue-50 border-blue-200";
      case "Average":
        return "text-yellow-600 bg-yellow-50 border-yellow-200";
      case "Needs Improvement":
        return "text-orange-600 bg-orange-50 border-orange-200";
      case "Poor":
        return "text-red-600 bg-red-50 border-red-200";
      default:
        return "text-gray-600 bg-gray-50 border-gray-200";
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "destructive";
      case "medium":
        return "default";
      case "low":
        return "secondary";
      default:
        return "outline";
    }
  };

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border/40 backdrop-blur-sm sticky top-0 z-50 bg-background/80">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <FileText className="h-5 w-5 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold">ATS Resume Analyzer</span>
            </div>
          </div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Hero Section */}
          {!analysis && (
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold mb-4">
                Optimize Your Resume for ATS
              </h1>
              <p className="text-xl text-muted-foreground mb-6">
                Get instant feedback on your resume's compatibility with Applicant Tracking Systems
              </p>
              <div className="flex justify-center gap-6 text-sm text-muted-foreground">
                <div className="flex items-center gap-2">
                  <Award className="h-4 w-4" />
                  <span>ATS Score</span>
                </div>
                <div className="flex items-center gap-2">
                  <Target className="h-4 w-4" />
                  <span>Keyword Analysis</span>
                </div>
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4" />
                  <span>Actionable Tips</span>
                </div>
              </div>
            </div>
          )}

          {/* Input Section */}
          {!analysis && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Upload Your Resume</CardTitle>
                <CardDescription>
                  Upload your resume in PDF, DOCX, or TXT format for instant analysis
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="resume-file">Resume File *</Label>
                  <div className="mt-2">
                    <input
                      ref={fileInputRef}
                      id="resume-file"
                      type="file"
                      accept=".pdf,.docx,.txt"
                      onChange={handleFileSelect}
                      className="hidden"
                    />
                    
                    {!selectedFile ? (
                      <div
                        onClick={() => fileInputRef.current?.click()}
                        className="border-2 border-dashed border-border rounded-lg p-8 text-center cursor-pointer hover:border-primary transition-colors"
                      >
                        <Upload className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
                        <p className="text-sm font-medium mb-1">Click to upload resume</p>
                        <p className="text-xs text-muted-foreground">
                          Supports PDF, DOCX, and TXT files
                        </p>
                      </div>
                    ) : (
                      <div className="border-2 border-primary rounded-lg p-4 flex items-center justify-between bg-primary/5">
                        <div className="flex items-center gap-3">
                          <FileText className="h-8 w-8 text-primary" />
                          <div>
                            <p className="font-medium text-sm">{selectedFile.name}</p>
                            <p className="text-xs text-muted-foreground">
                              {(selectedFile.size / 1024).toFixed(1)} KB
                            </p>
                          </div>
                        </div>
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={handleRemoveFile}
                          className="hover:bg-destructive/10"
                        >
                          <X className="h-4 w-4" />
                        </Button>
                      </div>
                    )}
                  </div>
                </div>

                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="role">Target Role (Optional)</Label>
                    <Input
                      id="role"
                      placeholder="e.g., Software Engineer, Data Scientist"
                      value={targetRole}
                      onChange={(e) => setTargetRole(e.target.value)}
                      className="mt-2"
                    />
                  </div>

                  <div>
                    <Label htmlFor="job-desc">Job Description (Optional)</Label>
                    <Input
                      id="job-desc"
                      placeholder="Paste job description keywords"
                      value={jobDescription}
                      onChange={(e) => setJobDescription(e.target.value)}
                      className="mt-2"
                    />
                  </div>
                </div>

                {error && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}

                <Button 
                  onClick={handleAnalyze} 
                  disabled={isAnalyzing || !selectedFile}
                  className="w-full"
                  size="lg"
                >
                  {isAnalyzing ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="mr-2 h-4 w-4" />
                      Analyze Resume
                    </>
                  )}
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Results Section */}
          {analysis && (
            <div className="space-y-6">
              {/* Back Button */}
              <Button onClick={() => setAnalysis(null)} variant="outline">
                <ArrowLeft className="mr-2 h-4 w-4" />
                Analyze Another Resume
              </Button>

              {/* Overall Score Card */}
              <Card className="border-2">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle>Overall Assessment</CardTitle>
                    <Badge className={getRatingColor(analysis.rating)} variant="outline">
                      {analysis.rating}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-6 mb-6">
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">Overall Score</span>
                        <span className="text-2xl font-bold">{analysis.overall_score}/100</span>
                      </div>
                      <Progress value={analysis.overall_score} className="h-3" />
                    </div>
                    <div>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium">ATS Compatibility</span>
                        <span className="text-2xl font-bold">{analysis.ats_score}/100</span>
                      </div>
                      <Progress value={analysis.ats_score} className="h-3" />
                    </div>
                  </div>
                  <p className="text-muted-foreground">{analysis.summary}</p>
                </CardContent>
              </Card>

              {/* Category Scores */}
              <Card>
                <CardHeader>
                  <CardTitle>Detailed Breakdown</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {Object.entries(analysis.category_scores).map(([category, score]) => (
                    <div key={category}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium capitalize">
                          {category.replace('_', ' ')}
                        </span>
                        <span className="text-sm font-bold">{score}/100</span>
                      </div>
                      <Progress value={score} className="h-2" />
                    </div>
                  ))}
                </CardContent>
              </Card>

              {/* Key Strengths */}
              {analysis.key_strengths.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                      Key Strengths
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {analysis.key_strengths.map((strength, idx) => (
                        <li key={idx} className="flex items-start gap-2">
                          <CheckCircle2 className="h-4 w-4 text-green-600 mt-0.5 flex-shrink-0" />
                          <span>{strength}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {/* Critical Issues */}
              {analysis.critical_issues.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertCircle className="h-5 w-5 text-orange-600" />
                      Critical Issues
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {analysis.critical_issues.map((issue, idx) => (
                      <div key={idx} className="border-l-4 border-orange-500 pl-4">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge variant={getSeverityColor(issue.severity)}>
                            {issue.severity}
                          </Badge>
                          <span className="font-medium">{issue.issue}</span>
                        </div>
                        <p className="text-sm text-muted-foreground">{issue.suggestion}</p>
                      </div>
                    ))}
                  </CardContent>
                </Card>
              )}

              {/* Keyword Analysis */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Target className="h-5 w-5" />
                    Keyword Analysis
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">Keyword Density</span>
                      <Badge variant="outline">{analysis.keyword_analysis.keyword_density}</Badge>
                    </div>
                  </div>
                  
                  {analysis.keyword_analysis.found_keywords.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2 text-sm">Found Keywords</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.keyword_analysis.found_keywords.map((keyword, idx) => (
                          <Badge key={idx} variant="secondary">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}

                  {analysis.keyword_analysis.missing_keywords.length > 0 && (
                    <div>
                      <h4 className="font-medium mb-2 text-sm">Recommended Keywords to Add</h4>
                      <div className="flex flex-wrap gap-2">
                        {analysis.keyword_analysis.missing_keywords.map((keyword, idx) => (
                          <Badge key={idx} variant="outline" className="border-orange-300">
                            {keyword}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Recommendations */}
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-blue-600" />
                    Recommendations
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ol className="space-y-3">
                    {analysis.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex gap-3">
                        <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">
                          {idx + 1}
                        </span>
                        <span className="pt-0.5">{rec}</span>
                      </li>
                    ))}
                  </ol>
                </CardContent>
              </Card>

              {/* Missing Sections & Formatting Issues */}
              {(analysis.missing_sections.length > 0 || analysis.formatting_issues.length > 0) && (
                <div className="grid md:grid-cols-2 gap-6">
                  {analysis.missing_sections.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Missing Sections</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {analysis.missing_sections.map((section, idx) => (
                            <li key={idx} className="flex items-center gap-2">
                              <AlertCircle className="h-4 w-4 text-orange-500" />
                              <span className="text-sm">{section}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}

                  {analysis.formatting_issues.length > 0 && (
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-base">Formatting Issues</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <ul className="space-y-2">
                          {analysis.formatting_issues.map((issue, idx) => (
                            <li key={idx} className="flex items-center gap-2">
                              <AlertCircle className="h-4 w-4 text-orange-500" />
                              <span className="text-sm">{issue}</span>
                            </li>
                          ))}
                        </ul>
                      </CardContent>
                    </Card>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
