"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Sparkles, Target, Zap, BarChart3, Brain, Mic, Clock, Award } from "lucide-react";
import Link from "next/link";

const companies = [
  { name: "Google", role: "Software Engineer", level: "L4", difficulty: "Hard", questions: 12, duration: "45 min", logo: "https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?w=100&h=100&fit=crop" },
  { name: "Meta", role: "Product Manager", level: "IC4", difficulty: "Hard", questions: 10, duration: "40 min", logo: "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=100&h=100&fit=crop" },
  { name: "Amazon", role: "Data Scientist", level: "L5", difficulty: "Medium", questions: 8, duration: "35 min", logo: "https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?w=100&h=100&fit=crop" },
  { name: "Microsoft", role: "Software Engineer", level: "62", difficulty: "Medium", questions: 10, duration: "40 min", logo: "https://images.unsplash.com/photo-1633419461186-7d40a38105ec?w=100&h=100&fit=crop" },
  { name: "Apple", role: "Design Lead", level: "ICT4", difficulty: "Hard", questions: 9, duration: "38 min", logo: "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=100&h=100&fit=crop" },
  { name: "Netflix", role: "Backend Engineer", level: "Senior", difficulty: "Hard", questions: 11, duration: "42 min", logo: "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=100&h=100&fit=crop" },
  { name: "Tesla", role: "Systems Engineer", level: "L3", difficulty: "Medium", questions: 10, duration: "40 min", logo: "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=100&h=100&fit=crop" },
  { name: "Spotify", role: "Product Designer", level: "Senior", difficulty: "Medium", questions: 8, duration: "35 min", logo: "https://images.unsplash.com/photo-1614680376593-902f74cf0d41?w=100&h=100&fit=crop" },
];

const features = [
  { icon: Brain, title: "AI-Powered Questions", description: "Get personalized questions based on the role and company culture" },
  { icon: Mic, title: "Voice Recognition", description: "Practice speaking naturally with advanced speech-to-text technology" },
  { icon: BarChart3, title: "Detailed Analytics", description: "Comprehensive feedback on your performance with actionable insights" },
  { icon: Target, title: "Company-Specific", description: "Tailored questions matching real interview patterns from top companies" },
];

export default function Home() {
  const [selectedRole, setSelectedRole] = useState<string>("all");
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>("all");

  const filteredCompanies = companies.filter((company) => {
    const roleMatch = selectedRole === "all" || company.role.toLowerCase().includes(selectedRole.toLowerCase());
    const difficultyMatch = selectedDifficulty === "all" || company.difficulty === selectedDifficulty;
    return roleMatch && difficultyMatch;
  });

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
          <nav className="hidden md:flex items-center gap-6">
            <a href="#features" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#templates" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Templates</a>
            <Link href="/resume" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Resume Analyzer</Link>
            <Button variant="ghost" size="sm">Sign In</Button>
            <Button size="sm" className="bg-primary hover:bg-primary/90">Get Started</Button>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20 md:py-32">
        <div className="max-w-4xl mx-auto text-center space-y-8">
          <Badge variant="secondary" className="px-4 py-1.5 text-xs font-medium">
            <Zap className="h-3 w-3 mr-1 inline" />
            Powered by Advanced AI
          </Badge>
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight bg-gradient-to-br from-foreground via-foreground to-muted-foreground bg-clip-text text-transparent">
            Master Your Next Interview
          </h1>
          <p className="text-xl md:text-2xl text-muted-foreground max-w-2xl mx-auto leading-relaxed">
            Practice with AI-powered mock interviews tailored to top companies. Get real-time feedback and ace your dream job.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center pt-4">
            <Link href="/interview">
              <Button size="lg" className="text-base px-8 h-12 bg-primary hover:bg-primary/90">
                Start Free Interview
                <Sparkles className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/resume">
              <Button size="lg" variant="outline" className="text-base px-8 h-12">
                Analyze Resume
              </Button>
            </Link>
          </div>
          <div className="flex items-center justify-center gap-8 pt-8 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span>10-45 min sessions</span>
            </div>
            <div className="flex items-center gap-2">
              <Award className="h-4 w-4" />
              <span>Instant feedback</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="container mx-auto px-4 py-20 border-t border-border/40">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Why Choose InterviewAI?</h2>
            <p className="text-lg text-muted-foreground">Everything you need to prepare for your interview</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <Card key={index} className="bg-card/50 border-border/40 hover:bg-card/80 transition-all hover:scale-105 duration-300">
                <CardHeader>
                  <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                    <feature.icon className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="text-lg">{feature.title}</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Templates Section */}
      <section id="templates" className="container mx-auto px-4 py-20 border-t border-border/40">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Company Interview Templates</h2>
            <p className="text-lg text-muted-foreground">Choose from our curated collection of company-specific interviews</p>
          </div>

          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            <Select value={selectedRole} onValueChange={setSelectedRole}>
              <SelectTrigger className="w-full sm:w-[200px]">
                <SelectValue placeholder="Select Role" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Roles</SelectItem>
                <SelectItem value="software">Software Engineer</SelectItem>
                <SelectItem value="product">Product Manager</SelectItem>
                <SelectItem value="data">Data Scientist</SelectItem>
                <SelectItem value="design">Designer</SelectItem>
              </SelectContent>
            </Select>

            <Select value={selectedDifficulty} onValueChange={setSelectedDifficulty}>
              <SelectTrigger className="w-full sm:w-[200px]">
                <SelectValue placeholder="Difficulty" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Levels</SelectItem>
                <SelectItem value="Easy">Easy</SelectItem>
                <SelectItem value="Medium">Medium</SelectItem>
                <SelectItem value="Hard">Hard</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Company Cards Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredCompanies.map((company, index) => (
              <Card key={index} className="group hover:shadow-xl transition-all duration-300 hover:scale-105 bg-card/50 border-border/40 overflow-hidden">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between mb-3">
                    <div className="h-14 w-14 rounded-lg overflow-hidden bg-muted">
                      <img src={company.logo} alt={company.name} className="h-full w-full object-cover" />
                    </div>
                    <Badge variant={company.difficulty === "Hard" ? "destructive" : "secondary"} className="text-xs">
                      {company.difficulty}
                    </Badge>
                  </div>
                  <CardTitle className="text-xl">{company.name}</CardTitle>
                  <CardDescription className="text-sm">{company.role} · {company.level}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <Target className="h-4 w-4" />
                      {company.questions} questions
                    </span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {company.duration}
                    </span>
                  </div>
                  <Link href="/interview">
                    <Button className="w-full group-hover:bg-primary group-hover:text-primary-foreground transition-colors">
                      Start Interview
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border/40 mt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-2">
              <div className="h-6 w-6 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center">
                <Sparkles className="h-4 w-4 text-primary-foreground" />
              </div>
              <span className="font-semibold">InterviewAI</span>
            </div>
            <p className="text-sm text-muted-foreground">© 2024 InterviewAI. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}