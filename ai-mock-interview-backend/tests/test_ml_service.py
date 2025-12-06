import pytest
import os
import sys
import numpy as np

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from ml_service import InterviewAnalyzer
from feature_extraction import ResponseFeatureExtractor

class TestFeatureExtraction:
    """Test feature extraction functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.extractor = ResponseFeatureExtractor()
    
    def test_basic_stats_extraction(self):
        """Test basic text statistics extraction"""
        text = "This is a test response with multiple sentences. It contains technical terms like API and database."
        
        features = self.extractor._extract_basic_stats(text)
        
        assert features['word_count'] > 0
        assert features['sentence_count'] == 2
        assert features['character_count'] > 0
        assert features['avg_word_length'] > 0
        assert 0 <= features['unique_word_ratio'] <= 1
    
    def test_filler_words_detection(self):
        """Test filler words detection"""
        text_with_fillers = "Um, like, I think the answer is, you know, actually quite simple."
        text_without_fillers = "The answer is quite simple and straightforward."
        
        features_with = self.extractor._analyze_filler_words(text_with_fillers)
        features_without = self.extractor._analyze_filler_words(text_without_fillers)
        
        assert features_with['filler_word_count'] > features_without['filler_word_count']
        assert features_with['filler_word_ratio'] > features_without['filler_word_ratio']
    
    def test_technical_terms_analysis(self):
        """Test technical terms detection"""
        technical_text = "REST API uses HTTP methods and JSON data format for database interactions."
        non_technical_text = "I like to eat pizza and watch movies on weekends."
        
        tech_features = self.extractor._analyze_technical_terms(technical_text, 'technical_software')
        non_tech_features = self.extractor._analyze_technical_terms(non_technical_text, 'technical_software')
        
        assert tech_features['technical_term_count'] > non_tech_features['technical_term_count']
        assert tech_features['technical_term_ratio'] > non_tech_features['technical_term_ratio']
    
    def test_confidence_analysis(self):
        """Test confidence indicators detection"""
        confident_text = "I am absolutely certain that this is the correct approach."
        uncertain_text = "I think maybe this might be the right answer, probably."
        
        confident_features = self.extractor._analyze_confidence(confident_text)
        uncertain_features = self.extractor._analyze_confidence(uncertain_text)
        
        assert confident_features['confidence_score'] > uncertain_features['confidence_score']
        assert confident_features['confidence_indicators_positive'] > 0
        assert uncertain_features['confidence_indicators_negative'] > 0
    
    def test_response_structure_analysis(self):
        """Test response structure detection"""
        structured_text = "First, let me explain the context. Then, I will describe my approach. Finally, I'll discuss the results and outcomes."
        unstructured_text = "It's complicated and involves various things."
        
        structured_features = self.extractor._analyze_response_structure(structured_text)
        unstructured_features = self.extractor._analyze_response_structure(unstructured_text)
        
        assert structured_features['structure_score'] > unstructured_features['structure_score']
        assert structured_features['has_overall_structure'] == True
        assert unstructured_features['has_overall_structure'] == False
    
    def test_relevance_calculation(self):
        """Test relevance score calculation"""
        question = "Explain what REST API is and how it works"
        relevant_response = "REST API is an architectural style that uses HTTP methods to interact with resources"
        irrelevant_response = "I like to eat pizza and play video games"
        
        relevant_features = self.extractor._analyze_relevance(relevant_response, question)
        irrelevant_features = self.extractor._analyze_relevance(irrelevant_response, question)
        
        assert relevant_features['relevance_score'] > irrelevant_features['relevance_score']
        assert relevant_features['keyword_overlap_ratio'] > irrelevant_features['keyword_overlap_ratio']
    
    def test_empty_text_handling(self):
        """Test handling of empty or invalid text"""
        empty_features = self.extractor.extract_all_features("", "Test question")
        
        assert empty_features['word_count'] == 0
        assert empty_features['filler_word_count'] == 0
        assert empty_features['technical_term_count'] == 0

class TestMLService:
    """Test ML service functionality"""
    
    def setup_method(self):
        """Setup test environment"""
        self.analyzer = InterviewAnalyzer()
    
    def test_analyze_response_basic(self):
        """Test basic response analysis"""
        response_text = "REST API is an architectural style that uses HTTP methods like GET, POST, PUT, and DELETE to interact with resources."
        question_text = "Explain what REST API is"
        
        result = self.analyzer.analyze_response(response_text, question_text, 'technical_software')
        
        assert 'overall_score' in result
        assert 'rating' in result
        assert 'scores' in result
        assert 'features' in result
        
        assert 0 <= result['overall_score'] <= 10
        assert result['rating'] in ['excellent', 'good', 'average', 'poor']
        
        scores = result['scores']
        assert 'content_quality' in scores
        assert 'communication' in scores
        assert 'confidence' in scores
        assert 'technical_accuracy' in scores
    
    def test_analyze_response_different_types(self):
        """Test analysis for different interview types"""
        technical_response = "Binary search works by repeatedly dividing the search space in half. It has O(log n) time complexity."
        behavioral_response = "In my previous role, I faced a challenging deadline. I organized the team, prioritized tasks, and we delivered on time."
        
        tech_result = self.analyzer.analyze_response(technical_response, "Explain binary search", 'technical_software')
        behavioral_result = self.analyzer.analyze_response(behavioral_response, "Tell me about a challenge", 'behavioral')
        
        # Technical response should score higher on technical accuracy for technical interview
        assert tech_result['scores']['technical_accuracy'] >= behavioral_result['scores']['technical_accuracy']
    
    def test_score_to_rating_conversion(self):
        """Test score to rating conversion"""
        test_cases = [
            (9.5, 'excellent'),
            (8.0, 'good'),
            (6.0, 'average'),
            (3.0, 'poor')
        ]
        
        for score, expected_rating in test_cases:
            rating = self.analyzer._score_to_rating(score)
            assert rating == expected_rating
    
    def test_feedback_generation(self):
        """Test feedback suggestions generation"""
        # Test with a good response
        good_response = "REST API is an architectural style that uses HTTP methods. For example, GET retrieves data, POST creates new resources."
        
        analysis = self.analyzer.analyze_response(good_response, "Explain REST API", 'technical_software')
        feedback = self.analyzer.generate_feedback_suggestions(analysis)
        
        assert isinstance(feedback, list)
        assert len(feedback) > 0
        
        for item in feedback:
            assert 'type' in item
            assert 'category' in item
            assert 'message' in item
            assert item['type'] in ['strength', 'improvement']
    
    def test_batch_analysis(self):
        """Test batch analysis functionality"""
        responses = [
            {
                'response_text': 'Good technical answer with proper terminology',
                'question_text': 'Technical question',
                'interview_type': 'technical_software'
            },
            {
                'response_text': 'Structured behavioral response with specific example',
                'question_text': 'Behavioral question',
                'interview_type': 'behavioral'
            }
        ]
        
        results = self.analyzer.batch_analyze(responses)
        
        assert len(results) == 2
        for result in results:
            assert 'overall_score' in result
            assert 'rating' in result
    
    def test_improvement_recommendations(self):
        """Test improvement recommendations generation"""
        # Create mock analysis results
        session_analyses = [
            {
                'overall_score': 6.5,
                'scores': {
                    'content_quality': 7.0,
                    'communication': 5.0,
                    'confidence': 6.0,
                    'technical_accuracy': 8.0
                }
            },
            {
                'overall_score': 5.5,
                'scores': {
                    'content_quality': 6.0,
                    'communication': 4.0,
                    'confidence': 5.0,
                    'technical_accuracy': 7.0
                }
            }
        ]
        
        recommendations = self.analyzer.get_improvement_recommendations(session_analyses)
        
        assert 'overall_score' in recommendations
        assert 'strongest_area' in recommendations
        assert 'weakest_area' in recommendations
        assert 'specific_recommendations' in recommendations
        
        # Communication should be the weakest area
        assert recommendations['weakest_area'] == 'communication'
    
    def test_rule_based_fallback(self):
        """Test rule-based analysis when ML model is not available"""
        # Create analyzer without ML model
        analyzer_no_ml = InterviewAnalyzer(model_path='nonexistent_model.pkl')
        
        response_text = "This is a comprehensive answer with technical terms like API, database, and algorithm."
        result = analyzer_no_ml.analyze_response(response_text, "Technical question", 'technical_software')
        
        assert 'overall_score' in result
        assert 'rating' in result
        assert result['ml_prediction']['method'] == 'rule_based'

class TestModelTraining:
    """Test model training functionality"""
    
    def test_training_data_generation(self):
        """Test training data generation"""
        # This would test the model training module
        # For now, we'll test that the module can be imported
        try:
            from model_training import InterviewResponseClassifier
            classifier = InterviewResponseClassifier()
            assert classifier is not None
        except ImportError:
            pytest.skip("Model training module not available")
    
    def test_feature_consistency(self):
        """Test that feature extraction is consistent"""
        extractor = ResponseFeatureExtractor()
        
        text = "REST API is an architectural style that uses HTTP methods."
        
        # Extract features multiple times
        features1 = extractor.extract_all_features(text, "Test question", 'technical_software')
        features2 = extractor.extract_all_features(text, "Test question", 'technical_software')
        
        # Results should be identical
        assert features1 == features2

if __name__ == "__main__":
    pytest.main([__file__, "-v"])