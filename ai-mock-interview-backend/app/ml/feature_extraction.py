"""Feature extraction for interview response analysis"""

import re
import nltk
from textblob import TextBlob
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Download required NLTK data if not already present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer


class ResponseFeatureExtractor:
    """Extract features from interview responses for ML analysis"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        
        # Filler words commonly used in speech
        self.filler_words = {
            'um', 'uh', 'like', 'you know', 'so', 'well', 'actually', 'basically',
            'literally', 'totally', 'obviously', 'i mean', 'sort of', 'kind of'
        }
        
        # Technical terms for different domains
        self.technical_terms = {
            'technical_software': {
                'algorithm', 'data structure', 'api', 'database', 'framework', 'library',
                'object-oriented', 'functional', 'recursion', 'iteration', 'complexity',
                'optimization', 'debugging', 'testing', 'deployment', 'version control',
                'git', 'sql', 'nosql', 'rest', 'json', 'xml', 'http', 'https',
                'javascript', 'python', 'java', 'c++', 'react', 'node', 'docker',
                'kubernetes', 'aws', 'cloud', 'microservices', 'authentication',
                'authorization', 'encryption', 'security', 'performance', 'scalability'
            },
            'behavioral': {
                'leadership', 'teamwork', 'communication', 'collaboration', 'problem-solving',
                'decision-making', 'conflict resolution', 'time management', 'priority',
                'deadline', 'responsibility', 'accountability', 'initiative', 'motivation',
                'adaptability', 'flexibility', 'learning', 'growth', 'feedback',
                'improvement', 'challenge', 'success', 'failure', 'lesson', 'experience'
            }
        }
        
        # Confidence indicators
        self.confidence_positive = {
            'definitely', 'certainly', 'absolutely', 'confident', 'sure', 'positive',
            'know', 'believe', 'understand', 'clear', 'obvious', 'simple', 'straightforward'
        }
        
        self.confidence_negative = {
            'maybe', 'perhaps', 'possibly', 'might', 'could', 'unsure', 'uncertain',
            'confused', 'difficult', 'complicated', 'not sure', 'i think', 'i guess',
            'probably', 'hopefully', 'i believe'
        }
        
        # Structure indicators
        self.structure_words = {
            'first', 'second', 'third', 'finally', 'next', 'then', 'after', 'before',
            'initially', 'subsequently', 'furthermore', 'moreover', 'however', 'therefore',
            'in conclusion', 'to summarize', 'overall', 'specifically', 'for example'
        }
    
    def extract_all_features(self, response_text, question_text, interview_type='general'):
        """Extract all features from a response"""
        if not response_text or not response_text.strip():
            return self._get_empty_features()
        
        features = {}
        
        # Basic text statistics
        features.update(self._extract_basic_stats(response_text))
        
        # Linguistic features
        features.update(self._analyze_filler_words(response_text))
        features.update(self._analyze_technical_terms(response_text, interview_type))
        features.update(self._analyze_confidence(response_text))
        features.update(self._analyze_response_structure(response_text))
        features.update(self._analyze_sentiment(response_text))
        
        # Question relevance
        features.update(self._analyze_relevance(response_text, question_text))
        
        return features
    
    def _extract_basic_stats(self, text):
        """Extract basic text statistics"""
        words = word_tokenize(text.lower())
        sentences = sent_tokenize(text)
        
        word_count = len([w for w in words if w.isalpha()])
        sentence_count = len(sentences)
        character_count = len(text)
        
        avg_word_length = np.mean([len(w) for w in words if w.isalpha()]) if word_count > 0 else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        unique_words = set([w for w in words if w.isalpha()])
        unique_word_ratio = len(unique_words) / word_count if word_count > 0 else 0
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'character_count': character_count,
            'avg_word_length': avg_word_length,
            'avg_sentence_length': avg_sentence_length,
            'unique_word_ratio': unique_word_ratio
        }
    
    def _analyze_filler_words(self, text):
        """Analyze filler word usage"""
        text_lower = text.lower()
        
        filler_count = 0
        for filler in self.filler_words:
            filler_count += len(re.findall(r'\b' + re.escape(filler) + r'\b', text_lower))
        
        words = word_tokenize(text_lower)
        word_count = len([w for w in words if w.isalpha()])
        
        filler_ratio = filler_count / word_count if word_count > 0 else 0
        
        return {
            'filler_word_count': filler_count,
            'filler_word_ratio': filler_ratio
        }
    
    def _analyze_technical_terms(self, text, interview_type):
        """Analyze technical term usage"""
        text_lower = text.lower()
        
        # Get relevant technical terms based on interview type
        relevant_terms = self.technical_terms.get(interview_type, set())
        
        technical_count = 0
        for term in relevant_terms:
            technical_count += len(re.findall(r'\b' + re.escape(term) + r'\b', text_lower))
        
        words = word_tokenize(text_lower)
        word_count = len([w for w in words if w.isalpha()])
        
        technical_ratio = technical_count / word_count if word_count > 0 else 0
        
        return {
            'technical_term_count': technical_count,
            'technical_term_ratio': technical_ratio
        }
    
    def _analyze_confidence(self, text):
        """Analyze confidence indicators"""
        text_lower = text.lower()
        
        positive_count = 0
        for indicator in self.confidence_positive:
            positive_count += len(re.findall(r'\b' + re.escape(indicator) + r'\b', text_lower))
        
        negative_count = 0
        for indicator in self.confidence_negative:
            negative_count += len(re.findall(r'\b' + re.escape(indicator) + r'\b', text_lower))
        
        # Calculate confidence score (0-1)
        total_indicators = positive_count + negative_count
        confidence_score = positive_count / total_indicators if total_indicators > 0 else 0.5
        
        return {
            'confidence_indicators_positive': positive_count,
            'confidence_indicators_negative': negative_count,
            'confidence_score': confidence_score
        }
    
    def _analyze_response_structure(self, text):
        """Analyze response structure"""
        text_lower = text.lower()
        
        structure_count = 0
        for indicator in self.structure_words:
            structure_count += len(re.findall(r'\b' + re.escape(indicator) + r'\b', text_lower))
        
        sentences = sent_tokenize(text)
        sentence_count = len(sentences)
        
        structure_ratio = structure_count / sentence_count if sentence_count > 0 else 0
        
        # Check for overall structure patterns
        has_introduction = any(word in text_lower for word in ['first', 'initially', 'to begin'])
        has_conclusion = any(word in text_lower for word in ['finally', 'in conclusion', 'overall'])
        has_examples = any(word in text_lower for word in ['for example', 'such as', 'like when'])
        
        structure_score = (structure_ratio + has_introduction + has_conclusion + has_examples) / 4
        
        return {
            'structure_indicators': structure_count,
            'structure_ratio': structure_ratio,
            'has_introduction': has_introduction,
            'has_conclusion': has_conclusion,
            'has_examples': has_examples,
            'has_overall_structure': has_introduction and has_conclusion,
            'structure_score': structure_score
        }
    
    def _analyze_sentiment(self, text):
        """Analyze sentiment of the response"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1
        
        # NLTK VADER sentiment
        vader_scores = self.sentiment_analyzer.polarity_scores(text)
        
        return {
            'sentiment_polarity': polarity,
            'sentiment_subjectivity': subjectivity,
            'sentiment_compound': vader_scores['compound'],
            'sentiment_positive': vader_scores['pos'],
            'sentiment_negative': vader_scores['neg'],
            'sentiment_neutral': vader_scores['neu']
        }
    
    def _analyze_relevance(self, response_text, question_text):
        """Analyze how relevant the response is to the question"""
        if not question_text:
            return {'relevance_score': 0.5, 'keyword_overlap_ratio': 0}
        
        # Tokenize and clean both texts
        response_words = set([w.lower() for w in word_tokenize(response_text) 
                            if w.isalpha() and w.lower() not in self.stop_words])
        question_words = set([w.lower() for w in word_tokenize(question_text) 
                            if w.isalpha() and w.lower() not in self.stop_words])
        
        # Calculate keyword overlap
        overlap = len(response_words.intersection(question_words))
        keyword_overlap_ratio = overlap / len(question_words) if len(question_words) > 0 else 0
        
        # Simple relevance score based on keyword overlap
        relevance_score = min(keyword_overlap_ratio * 2, 1.0)  # Cap at 1.0
        
        return {
            'relevance_score': relevance_score,
            'keyword_overlap_ratio': keyword_overlap_ratio
        }
    
    def _get_empty_features(self):
        """Return empty features for invalid input"""
        return {
            'word_count': 0,
            'sentence_count': 0,
            'character_count': 0,
            'avg_word_length': 0,
            'avg_sentence_length': 0,
            'unique_word_ratio': 0,
            'filler_word_count': 0,
            'filler_word_ratio': 0,
            'technical_term_count': 0,
            'technical_term_ratio': 0,
            'confidence_indicators_positive': 0,
            'confidence_indicators_negative': 0,
            'confidence_score': 0,
            'structure_indicators': 0,
            'structure_ratio': 0,
            'has_introduction': False,
            'has_conclusion': False,
            'has_examples': False,
            'has_overall_structure': False,
            'structure_score': 0,
            'sentiment_polarity': 0,
            'sentiment_subjectivity': 0,
            'sentiment_compound': 0,
            'sentiment_positive': 0,
            'sentiment_negative': 0,
            'sentiment_neutral': 0,
            'relevance_score': 0,
            'keyword_overlap_ratio': 0
        }