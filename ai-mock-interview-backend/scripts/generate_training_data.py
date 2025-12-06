#!/usr/bin/env python3
"""Generate training data for the interview ML model"""

import pandas as pd
import random
import os
from pathlib import Path

class TrainingDataGenerator:
    def __init__(self):
        self.technical_responses = {
            "excellent": [
                "I use a hash map to store the complement of each number as I iterate through the array. For each element, I check if its complement exists in the hash map. If it does, I return the indices. The time complexity is O(n) and space complexity is O(n).",
                "Object-oriented programming has four main principles: encapsulation, inheritance, polymorphism, and abstraction. Encapsulation bundles data and methods together, inheritance allows classes to inherit properties from parent classes, polymorphism enables objects to take multiple forms, and abstraction hides complex implementation details.",
                "A REST API follows specific principles: stateless communication, uniform interface, client-server architecture, cacheable responses, and layered system. It uses HTTP methods like GET, POST, PUT, DELETE to perform CRUD operations on resources identified by URLs.",
                "Big O notation describes the upper bound of algorithm complexity. O(1) is constant time, O(n) is linear, O(n²) is quadratic, and O(log n) is logarithmic. It helps us analyze how algorithm performance scales with input size.",
            ],
            "good": [
                "I would use a hash map to solve the two-sum problem. I iterate through the array and for each number, I check if the target minus that number exists in the hash map. If it does, I found the pair.",
                "OOP has four main concepts: encapsulation keeps data private, inheritance lets you extend classes, polymorphism allows different implementations of the same method, and abstraction hides complexity.",
                "REST API uses HTTP methods to interact with resources. GET retrieves data, POST creates new data, PUT updates existing data, and DELETE removes data. URLs identify the resources.",
                "Big O notation measures algorithm efficiency. O(1) is fastest for constant time, O(n) increases linearly with input size, and O(n²) grows quadratically which is slower for large inputs.",
            ],
            "average": [
                "I think you can use a loop to check each pair of numbers until you find the ones that add up to the target. It might take some time but it works.",
                "Object-oriented programming has classes and objects. Classes are like blueprints and objects are instances of classes. You can inherit from other classes too.",
                "REST API is a way to communicate between client and server using HTTP. You send requests and get responses back with data.",
                "Big O notation is about how fast algorithms run. Some are faster than others depending on the input size.",
            ],
            "poor": [
                "Um, I'm not really sure about the two-sum problem. Maybe you just try all combinations?",
                "OOP is about objects and classes, I think. Not really sure about the details.",
                "REST API is something about web services, but I don't know much about it.",
                "Big O is about algorithm speed, but I don't remember the details.",
            ]
        }
        
        self.behavioral_responses = {
            "excellent": [
                "In my previous team project, we had a disagreement about the technical approach. I initiated a team meeting where I listened to everyone's concerns, presented data-driven analysis of different solutions, and facilitated a collaborative decision-making process. We reached a consensus that combined the best aspects of different approaches, resulting in a 20% performance improvement.",
                "When I encountered a challenging bug in our web application, I systematically approached it by reproducing the issue, analyzing logs, and using debugging tools. I broke down the problem into smaller parts, researched similar issues, and collaborated with senior developers. After two days of investigation, I discovered it was a race condition and implemented a proper synchronization solution.",
                "I demonstrate leadership by taking initiative on projects, mentoring junior team members, and facilitating communication between different stakeholders. In my last internship, I led a team of 4 students to develop a mobile app, where I organized daily standups, delegated tasks based on individual strengths, and ensured we delivered on time.",
            ],
            "good": [
                "When we had a conflict in our group project, I tried to understand both perspectives and suggested we vote on the best approach. We discussed the pros and cons and came to an agreement.",
                "I faced a difficult coding problem last semester. I spent time researching online, asked my professor for guidance, and worked through it step by step until I found the solution.",
                "I show leadership by volunteering for challenging tasks and helping my teammates when they're stuck. I try to keep everyone motivated and focused on our goals.",
            ],
            "average": [
                "When there was a disagreement in my team, I just went along with what the majority wanted to avoid conflict.",
                "When I face difficult problems, I usually search online for solutions or ask someone for help.",
                "I'm not really a natural leader, but I try to do my part in group projects.",
            ],
            "poor": [
                "I don't really like conflicts, so I usually just stay quiet when there are disagreements.",
                "I get frustrated with difficult problems and sometimes give up if I can't solve them quickly.",
                "I prefer to work alone rather than lead others.",
            ]
        }
        
        self.questions = {
            "technical": [
                "Explain the two-sum problem and how you would solve it efficiently.",
                "What are the four pillars of object-oriented programming?",
                "How does a REST API work and what are HTTP methods?",
                "Explain Big O notation and give examples of different complexities.",
                "What is the difference between SQL and NoSQL databases?",
                "How does garbage collection work in programming languages?",
                "Explain the concept of recursion with an example.",
                "What are design patterns and can you name a few?",
            ],
            "behavioral": [
                "Tell me about a time when you had to work with a difficult team member.",
                "Describe a challenging problem you solved and your approach.",
                "Give an example of when you demonstrated leadership skills.",
                "Tell me about a time you failed and what you learned from it.",
                "How do you handle stress and tight deadlines?",
                "Describe a time when you had to learn something new quickly.",
                "Tell me about a time you disagreed with your supervisor.",
                "How do you prioritize tasks when everything seems urgent?",
            ]
        }
    
    def generate_training_data(self, num_samples=1000):
        """Generate training data with realistic interview responses"""
        data = []
        
        for _ in range(num_samples):
            # Randomly choose question type
            question_type = random.choice(["technical", "behavioral"])
            question = random.choice(self.questions[question_type])
            
            # Randomly choose performance level
            performance_level = random.choice(["excellent", "good", "average", "poor"])
            
            # Get appropriate response
            if question_type == "technical":
                response = random.choice(self.technical_responses[performance_level])
            else:
                response = random.choice(self.behavioral_responses[performance_level])
            
            # Add some variation to responses
            response = self._add_variation(response, performance_level)
            
            # Create training sample
            sample = {
                "question": question,
                "response": response,
                "question_type": question_type,
                "performance_level": performance_level,
                "confidence_score": self._generate_confidence_score(performance_level),
                "technical_accuracy": self._generate_technical_score(performance_level, question_type),
                "communication_clarity": self._generate_communication_score(performance_level),
                "overall_score": self._generate_overall_score(performance_level)
            }
            
            data.append(sample)
        
        return pd.DataFrame(data)
    
    def _add_variation(self, response, performance_level):
        """Add realistic variations to responses"""
        filler_words = ["um", "uh", "like", "you know", "so", "well"]
        
        if performance_level == "poor":
            # Add more filler words and hesitation
            words = response.split()
            for i in range(0, len(words), 3):
                if random.random() < 0.3:
                    words.insert(i, random.choice(filler_words))
            return " ".join(words)
        elif performance_level == "average":
            # Add occasional filler words
            if random.random() < 0.2:
                return f"{random.choice(filler_words)}, {response}"
        
        return response
    
    def _generate_confidence_score(self, performance_level):
        """Generate confidence scores based on performance level"""
        score_ranges = {
            "excellent": (0.8, 1.0),
            "good": (0.6, 0.8),
            "average": (0.4, 0.6),
            "poor": (0.1, 0.4)
        }
        min_score, max_score = score_ranges[performance_level]
        return round(random.uniform(min_score, max_score), 2)
    
    def _generate_technical_score(self, performance_level, question_type):
        """Generate technical accuracy scores"""
        if question_type == "behavioral":
            return None
        
        score_ranges = {
            "excellent": (0.85, 1.0),
            "good": (0.65, 0.85),
            "average": (0.4, 0.65),
            "poor": (0.1, 0.4)
        }
        min_score, max_score = score_ranges[performance_level]
        return round(random.uniform(min_score, max_score), 2)
    
    def _generate_communication_score(self, performance_level):
        """Generate communication clarity scores"""
        score_ranges = {
            "excellent": (0.8, 1.0),
            "good": (0.6, 0.8),
            "average": (0.4, 0.6),
            "poor": (0.2, 0.4)
        }
        min_score, max_score = score_ranges[performance_level]
        return round(random.uniform(min_score, max_score), 2)
    
    def _generate_overall_score(self, performance_level):
        """Generate overall performance scores"""
        score_ranges = {
            "excellent": (0.8, 1.0),
            "good": (0.6, 0.8),
            "average": (0.4, 0.6),
            "poor": (0.1, 0.4)
        }
        min_score, max_score = score_ranges[performance_level]
        return round(random.uniform(min_score, max_score), 2)

def main():
    """Generate and save training data"""
    print("🤖 Generating training data for ML model...")
    
    # Create necessary directories
    os.makedirs("data", exist_ok=True)
    os.makedirs("models", exist_ok=True)
    
    # Generate training data
    generator = TrainingDataGenerator()
    df = generator.generate_training_data(num_samples=2000)
    
    # Save to CSV
    df.to_csv("data/training_data.csv", index=False)
    print(f"✅ Generated {len(df)} training samples and saved to data/training_data.csv")
    
    # Display sample data
    print("\n📊 Sample data:")
    print(df.head())
    
    # Display distribution
    print("\n📈 Performance level distribution:")
    print(df['performance_level'].value_counts())
    
    print("\n📈 Question type distribution:")
    print(df['question_type'].value_counts())
    
    print("\n🎉 Training data generation completed!")

if __name__ == "__main__":
    main()