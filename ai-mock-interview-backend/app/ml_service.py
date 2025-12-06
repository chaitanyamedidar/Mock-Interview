import joblib
import numpy as np
from typing import Dict, Any, List
from .ml.feature_extraction import ResponseFeatureExtractor
import os
import logging

class InterviewAnalyzer:
    """
    Service class for analyzing interview responses using trained ML model
    """
    
    def __init__(self, model_path='models/interview_classifier.pkl'):
        """
        Load trained ML model and dependencies
        """
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.feature_extractor = ResponseFeatureExtractor()
        
        # Try to load trained model
        try:
            if os.path.exists(model_path):
                model_data = joblib.load(model_path)
                self.model = model_data.get('model')
                self.scaler = model_data.get('scaler')
                self.feature_names = model_data.get('feature_names')
                self.feature_extractor = model_data.get('feature_extractor', self.feature_extractor)
                print(f"ML Model loaded successfully from {model_path}")
            else:
                print(f"Model file not found at {model_path}. Using rule-based analysis.")
        except Exception as e:
            print(f"Error loading model: {e}")
            print("Falling back to rule-based analysis")
    
    def analyze_response(self, response_text: str, question_text: str = '', interview_type: str = 'technical_software') -> Dict[str, Any]:
        """
        Comprehensive analysis of a single interview response
        """
        # Extract features
        features = self.feature_extractor.extract_all_features(
            response_text, question_text, interview_type
        )
        
        # Get ML prediction if model is loaded
        if self.model and self.scaler:
            ml_prediction = self._get_ml_prediction(features)
        else:
            ml_prediction = self._get_rule_based_prediction(features)
        
        # Calculate individual scores
        scores = self._calculate_component_scores(features, response_text, interview_type)
        
        # Calculate overall score
        overall_score = (
            scores['content_quality'] * 0.35 +
            scores['communication'] * 0.25 +
            scores['confidence'] * 0.20 +
            scores['technical_accuracy'] * 0.20
        )
        
        # Determine rating
        rating = self._score_to_rating(overall_score)
        
        return {
            'overall_score': round(overall_score, 2),
            'rating': rating,
            'scores': scores,
            'ml_prediction': ml_prediction,
            'features': features,
            'interview_type': interview_type
        }
    
    def _get_ml_prediction(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get prediction from trained ML model
        """
        try:
            import pandas as pd
            
            # Convert to DataFrame with correct feature order
            X = pd.DataFrame([features])[self.feature_names]
            X = X.fillna(0)  # Handle any missing features
            
            # Scale
            X_scaled = self.scaler.transform(X)
            
            # Predict
            prediction = self.model.predict(X_scaled)[0]
            probabilities = self.model.predict_proba(X_scaled)[0]
            confidence = max(probabilities)
            
            # Get probability for each class
            class_names = self.model.classes_
            class_probabilities = dict(zip(class_names, probabilities))
            
            return {
                'prediction': prediction,
                'confidence': confidence,
                'class_probabilities': class_probabilities,
                'method': 'ml_model'
            }
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            return self._get_rule_based_prediction(features)
    
    def _get_rule_based_prediction(self, features: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback rule-based prediction when ML model is not available
        """
        score = 0
        max_score = 100
        
        # Word count scoring (20 points)
        word_count = features.get('word_count', 0)
        if word_count >= 80:
            score += 20
        elif word_count >= 50:
            score += 15
        elif word_count >= 30:
            score += 10
        elif word_count >= 15:
            score += 5
        
        # Filler words scoring (15 points)
        filler_ratio = features.get('filler_word_ratio', 0)
        if filler_ratio <= 0.02:  # Less than 2%
            score += 15
        elif filler_ratio <= 0.05:  # Less than 5%
            score += 10
        elif filler_ratio <= 0.1:  # Less than 10%
            score += 5
        
        # Technical terms scoring (20 points)
        tech_count = features.get('technical_term_count', 0)
        if tech_count >= 5:
            score += 20
        elif tech_count >= 3:
            score += 15
        elif tech_count >= 1:
            score += 10
        
        # Structure scoring (15 points)
        if features.get('has_overall_structure', False):
            score += 8
        if features.get('has_examples', False):
            score += 7
        
        # Confidence scoring (15 points)
        confidence_score = features.get('confidence_score', 0)
        if confidence_score >= 2:
            score += 15
        elif confidence_score >= 0:
            score += 10
        elif confidence_score >= -1:
            score += 5
        
        # Language complexity (15 points)
        vocab_diversity = features.get('vocabulary_diversity', 0)
        if vocab_diversity >= 0.7:
            score += 15
        elif vocab_diversity >= 0.5:
            score += 10
        elif vocab_diversity >= 0.3:
            score += 5
        
        # Convert to percentage
        percentage = (score / max_score) * 100
        
        # Determine rating
        if percentage >= 85:
            rating = 'excellent'
        elif percentage >= 70:
            rating = 'good'
        elif percentage >= 50:
            rating = 'average'
        else:
            rating = 'poor'
        
        return {
            'prediction': rating,
            'confidence': 0.8,  # Fixed confidence for rule-based
            'score_percentage': percentage,
            'method': 'rule_based'
        }
    
    def _calculate_component_scores(self, features: Dict[str, Any], response_text: str, interview_type: str) -> Dict[str, float]:
        """
        Calculate individual component scores
        """
        scores = {}
        
        # Content Quality Score (based on length, structure, examples)
        content_score = 0
        word_count = features.get('word_count', 0)
        
        # Length component (40%)
        if word_count >= 80:
            length_score = 10
        elif word_count >= 50:
            length_score = 8
        elif word_count >= 30:
            length_score = 6
        elif word_count >= 15:
            length_score = 4
        else:
            length_score = 2
        
        # Structure component (30%)
        structure_score = 0
        if features.get('has_overall_structure', False):
            structure_score += 3
        if features.get('has_examples', False):
            structure_score += 3
        if features.get('has_quantifiable_results', False):
            structure_score += 2
        if features.get('structure_score', 0) > 1:
            structure_score += 2
        
        # Relevance component (30%)
        relevance_score = features.get('relevance_score', 0.5) * 10
        
        content_score = (length_score * 0.4 + structure_score * 0.3 + relevance_score * 0.3)
        scores['content_quality'] = min(10, max(0, content_score))
        
        # Communication Score (based on filler words, sentence structure)
        communication_score = 10
        
        # Penalize filler words
        filler_ratio = features.get('filler_word_ratio', 0)
        if filler_ratio > 0.1:  # More than 10%
            communication_score -= 4
        elif filler_ratio > 0.05:  # More than 5%
            communication_score -= 2
        elif filler_ratio > 0.02:  # More than 2%
            communication_score -= 1
        
        # Reward good sentence structure
        avg_sentence_length = features.get('avg_sentence_length', 0)
        if 15 <= avg_sentence_length <= 25:  # Optimal range
            communication_score += 1
        elif avg_sentence_length < 8 or avg_sentence_length > 35:
            communication_score -= 1
        
        # Vocabulary diversity
        vocab_diversity = features.get('vocabulary_diversity', 0)
        if vocab_diversity >= 0.7:
            communication_score += 1
        elif vocab_diversity < 0.3:
            communication_score -= 1
        
        scores['communication'] = min(10, max(0, communication_score))
        
        # Confidence Score
        confidence_indicators = features.get('confidence_score', 0)
        base_confidence = 7  # Start with average
        
        if confidence_indicators >= 3:
            confidence_score = 9
        elif confidence_indicators >= 1:
            confidence_score = 8
        elif confidence_indicators >= 0:
            confidence_score = 7
        elif confidence_indicators >= -1:
            confidence_score = 5
        else:
            confidence_score = 3
        
        scores['confidence'] = confidence_score
        
        # Technical Accuracy Score (for technical interviews)
        if interview_type.startswith('technical'):
            tech_terms = features.get('technical_term_count', 0)
            tech_ratio = features.get('technical_term_ratio', 0)
            
            if tech_terms >= 5 and tech_ratio >= 0.05:
                tech_score = 9
            elif tech_terms >= 3 and tech_ratio >= 0.03:
                tech_score = 7
            elif tech_terms >= 1:
                tech_score = 5
            else:
                tech_score = 3
        else:
            # For behavioral interviews, focus on structure and examples
            if features.get('has_examples', False) and features.get('has_overall_structure', False):
                tech_score = 8
            elif features.get('has_examples', False) or features.get('has_overall_structure', False):
                tech_score = 6
            else:
                tech_score = 4
        
        scores['technical_accuracy'] = tech_score
        
        return scores
    
    def _score_to_rating(self, score: float) -> str:
        """
        Convert numerical score to rating category
        """
        if score >= 8.5:
            return "excellent"
        elif score >= 7.0:
            return "good"
        elif score >= 5.0:
            return "average"
        else:
            return "poor"
    
    def batch_analyze(self, responses: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Analyze multiple responses in batch
        """
        results = []
        for response_data in responses:
            result = self.analyze_response(
                response_data.get('response_text', ''),
                response_data.get('question_text', ''),
                response_data.get('interview_type', 'technical_software')
            )
            results.append(result)
        return results
    
    def generate_feedback_suggestions(self, analysis_result: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate specific feedback suggestions based on analysis
        """
        feedback = []
        features = analysis_result['features']
        scores = analysis_result['scores']
        
        # Content quality feedback
        if scores['content_quality'] < 6:
            if features.get('word_count', 0) < 30:
                feedback.append({
                    'type': 'improvement',
                    'category': 'content',
                    'message': 'Your response was quite brief. Try to provide more detailed explanations with specific examples and context.'
                })
            
            if not features.get('has_examples', False):
                feedback.append({
                    'type': 'improvement',
                    'category': 'content',
                    'message': 'Include specific examples to illustrate your points and make your answer more concrete and memorable.'
                })
        else:
            feedback.append({
                'type': 'strength',
                'category': 'content',
                'message': 'Good job providing detailed and well-structured content in your response.'
            })
        
        # Communication feedback
        if scores['communication'] < 6:
            filler_ratio = features.get('filler_word_ratio', 0)
            if filler_ratio > 0.05:
                feedback.append({
                    'type': 'improvement',
                    'category': 'communication',
                    'message': f'Try to reduce filler words (found {filler_ratio:.1%} of your speech). Practice pausing instead of using "um", "like", or "you know".'
                })
        else:
            feedback.append({
                'type': 'strength',
                'category': 'communication',
                'message': 'Clear and articulate communication with minimal filler words.'
            })
        
        # Confidence feedback
        if scores['confidence'] < 6:
            feedback.append({
                'type': 'improvement',
                'category': 'confidence',
                'message': 'Use more confident language. Replace uncertain phrases like "maybe" and "I think" with assertive statements like "I recommend" or "The best approach is".'
            })
        else:
            feedback.append({
                'type': 'strength',
                'category': 'confidence',
                'message': 'Confident and assertive delivery that demonstrates your expertise.'
            })
        
        # Technical accuracy feedback
        if scores['technical_accuracy'] < 6:
            if analysis_result['interview_type'].startswith('technical'):
                feedback.append({
                    'type': 'improvement',
                    'category': 'technical',
                    'message': 'Include more relevant technical terminology and demonstrate deeper technical knowledge in your response.'
                })
            else:
                feedback.append({
                    'type': 'improvement',
                    'category': 'structure',
                    'message': 'Structure your behavioral responses using the STAR method (Situation, Task, Action, Result) for better clarity.'
                })
        
        return feedback
    
    def get_improvement_recommendations(self, session_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate improvement recommendations based on multiple responses
        """
        if not session_analyses:
            return {}
        
        # Calculate averages
        avg_scores = {
            'content_quality': np.mean([a['scores']['content_quality'] for a in session_analyses]),
            'communication': np.mean([a['scores']['communication'] for a in session_analyses]),
            'confidence': np.mean([a['scores']['confidence'] for a in session_analyses]),
            'technical_accuracy': np.mean([a['scores']['technical_accuracy'] for a in session_analyses])
        }
        
        # Identify weakest areas
        weakest_area = min(avg_scores, key=avg_scores.get)
        strongest_area = max(avg_scores, key=avg_scores.get)
        
        recommendations = {
            'overall_score': np.mean([a['overall_score'] for a in session_analyses]),
            'strongest_area': strongest_area,
            'weakest_area': weakest_area,
            'avg_scores': avg_scores,
            'specific_recommendations': []
        }
        
        # Generate specific recommendations
        if avg_scores['content_quality'] < 6:
            recommendations['specific_recommendations'].append(
                "Focus on providing more comprehensive answers with specific examples and quantifiable results."
            )
        
        if avg_scores['communication'] < 6:
            recommendations['specific_recommendations'].append(
                "Practice reducing filler words and improving speech clarity through regular mock interviews."
            )
        
        if avg_scores['confidence'] < 6:
            recommendations['specific_recommendations'].append(
                "Work on confident delivery by practicing assertive language and avoiding uncertain phrases."
            )
        
        if avg_scores['technical_accuracy'] < 6:
            recommendations['specific_recommendations'].append(
                "Strengthen technical knowledge and practice explaining complex concepts clearly."
            )
        
        return recommendations

# Usage example
if __name__ == "__main__":
    analyzer = InterviewAnalyzer()
    
    sample_response = """
    REST API is an architectural style that uses HTTP methods like GET, POST, PUT, and DELETE 
    to interact with resources. It's stateless, meaning each request contains all the information 
    needed to process it. For example, when you make a GET request to /users/123, you're requesting 
    the user with ID 123. The server responds with the data in a format like JSON.
    """
    
    result = analyzer.analyze_response(
        sample_response,
        "Explain what REST API is and how it works",
        "technical_software"
    )
    
    print("Analysis Result:")
    print(f"Overall Score: {result['overall_score']}")
    print(f"Rating: {result['rating']}")
    print(f"Component Scores: {result['scores']}")
    
    # Generate feedback
    feedback = analyzer.generate_feedback_suggestions(result)
    print("\nFeedback:")
    for item in feedback:
        print(f"- {item['type'].upper()}: {item['message']}")