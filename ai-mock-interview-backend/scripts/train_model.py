#!/usr/bin/env python3
"""Train the interview assessment ML model"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import pickle
import os
import sys
from pathlib import Path

# Add the parent directory to the path to import our modules
sys.path.append(str(Path(__file__).parent.parent))

from app.ml.feature_extraction import ResponseFeatureExtractor

class InterviewModelTrainer:
    def __init__(self):
        self.feature_extractor = ResponseFeatureExtractor()
        self.vectorizer = TfidfVectorizer(max_features=500, stop_words='english', ngram_range=(1, 2))
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
    def prepare_features(self, df):
        """Extract features from the training data"""
        print("🔍 Extracting features from responses...")
        
        # Extract linguistic features
        features_list = []
        for idx, row in df.iterrows():
            question = row['question']
            response = row['response']
            question_type = row['question_type']
            
            # Extract features using our feature extractor
            features = self.feature_extractor.extract_all_features(response, question, question_type)
            features_list.append(features)
            
            if idx % 200 == 0:
                print(f"   Processed {idx}/{len(df)} responses")
        
        # Convert to DataFrame
        features_df = pd.DataFrame(features_list)
        
        # Add TF-IDF features for text analysis
        print("🔍 Computing TF-IDF features...")
        tfidf_features = self.vectorizer.fit_transform(df['response']).toarray()
        tfidf_df = pd.DataFrame(tfidf_features, columns=[f'tfidf_{i}' for i in range(tfidf_features.shape[1])])
        
        # Combine all features
        combined_features = pd.concat([features_df.reset_index(drop=True), tfidf_df.reset_index(drop=True)], axis=1)
        
        print(f"✅ Feature extraction completed. Total features: {len(combined_features.columns)}")
        return combined_features
    
    def train_model(self, training_data_path):
        """Train the interview assessment model"""
        print(f"📚 Loading training data from {training_data_path}")
        
        # Load data
        df = pd.read_csv(training_data_path)
        print(f"   Loaded {len(df)} training samples")
        
        # Prepare features
        X = self.prepare_features(df)
        
        # Prepare target variable (overall_score)
        y = df['overall_score'].values
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=df['performance_level']
        )
        
        print(f"📊 Training set size: {len(X_train)}")
        print(f"📊 Test set size: {len(X_test)}")
        
        # Scale features
        print("⚖️  Scaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        print("🤖 Training Random Forest model...")
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate model
        print("📈 Evaluating model performance...")
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        
        train_mse = mean_squared_error(y_train, train_pred)
        test_mse = mean_squared_error(y_test, test_pred)
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        # Cross-validation
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='r2')
        
        print(f"\n📊 Model Performance:")
        print(f"   Training MSE: {train_mse:.4f}")
        print(f"   Test MSE: {test_mse:.4f}")
        print(f"   Training MAE: {train_mae:.4f}")
        print(f"   Test MAE: {test_mae:.4f}")
        print(f"   Training R²: {train_r2:.4f}")
        print(f"   Test R²: {test_r2:.4f}")
        print(f"   Cross-validation R² (mean ± std): {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print(f"\n🎯 Top 15 Most Important Features:")
        for idx, row in feature_importance.head(15).iterrows():
            print(f"   {row['feature']}: {row['importance']:.4f}")
        
        # Performance by category
        self._analyze_performance_by_category(df, X_test, y_test, test_pred)
        
        return {
            'train_mse': train_mse,
            'test_mse': test_mse,
            'train_mae': train_mae,
            'test_mae': test_mae,
            'train_r2': train_r2,
            'test_r2': test_r2,
            'cv_r2_mean': cv_scores.mean(),
            'cv_r2_std': cv_scores.std(),
            'feature_importance': feature_importance
        }
    
    def _analyze_performance_by_category(self, df, X_test, y_test, test_pred):
        """Analyze model performance by different categories"""
        print(f"\n📋 Performance Analysis by Category:")
        
        # Get test indices
        test_indices = X_test.index
        test_df = df.iloc[test_indices].copy()
        test_df['predicted_score'] = test_pred
        test_df['actual_score'] = y_test
        test_df['error'] = np.abs(test_df['predicted_score'] - test_df['actual_score'])
        
        # Performance by question type
        print("   By Question Type:")
        for q_type in test_df['question_type'].unique():
            subset = test_df[test_df['question_type'] == q_type]
            mae = subset['error'].mean()
            r2 = r2_score(subset['actual_score'], subset['predicted_score'])
            print(f"     {q_type}: MAE={mae:.4f}, R²={r2:.4f} (n={len(subset)})")
        
        # Performance by performance level
        print("   By Performance Level:")
        for level in test_df['performance_level'].unique():
            subset = test_df[test_df['performance_level'] == level]
            mae = subset['error'].mean()
            r2 = r2_score(subset['actual_score'], subset['predicted_score'])
            print(f"     {level}: MAE={mae:.4f}, R²={r2:.4f} (n={len(subset)})")
    
    def save_model(self, model_path):
        """Save the trained model and preprocessing components"""
        print(f"💾 Saving model to {model_path}")
        
        # Create models directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Save all components
        model_components = {
            'model': self.model,
            'vectorizer': self.vectorizer,
            'scaler': self.scaler,
            'feature_extractor': self.feature_extractor
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(model_components, f)
        
        print(f"✅ Model saved successfully!")
    
    def load_model(self, model_path):
        """Load a trained model"""
        print(f"📂 Loading model from {model_path}")
        
        with open(model_path, 'rb') as f:
            model_components = pickle.load(f)
        
        self.model = model_components['model']
        self.vectorizer = model_components['vectorizer']
        self.scaler = model_components['scaler']
        self.feature_extractor = model_components['feature_extractor']
        
        print("✅ Model loaded successfully!")
    
    def predict_score(self, response, question, question_type):
        """Predict score for a single response"""
        # Extract features
        features = self.feature_extractor.extract_all_features(response, question, question_type)
        features_df = pd.DataFrame([features])
        
        # Add TF-IDF features
        tfidf_features = self.vectorizer.transform([response]).toarray()
        tfidf_df = pd.DataFrame(tfidf_features, columns=[f'tfidf_{i}' for i in range(tfidf_features.shape[1])])
        
        # Combine features
        combined_features = pd.concat([features_df.reset_index(drop=True), tfidf_df], axis=1)
        
        # Scale features
        features_scaled = self.scaler.transform(combined_features)
        
        # Predict
        score = self.model.predict(features_scaled)[0]
        
        # Ensure score is between 0 and 1
        return max(0.0, min(1.0, score))

def main():
    """Main training pipeline"""
    print("🚀 Starting ML model training pipeline...")
    print("=" * 60)
    
    # Check if training data exists
    training_data_path = "data/training_data.csv"
    if not os.path.exists(training_data_path):
        print(f"❌ Training data not found at {training_data_path}")
        print("   Please run: python scripts/generate_training_data.py")
        return
    
    # Initialize trainer
    trainer = InterviewModelTrainer()
    
    # Train model
    results = trainer.train_model(training_data_path)
    
    # Save model
    trainer.save_model("models/interview_classifier.pkl")
    
    # Test the model with sample predictions
    print("\n🧪 Testing model with sample predictions:")
    print("=" * 60)
    
    test_cases = [
        {
            "response": "I use a hash map to solve the two-sum problem efficiently. The time complexity is O(n) and space complexity is O(n). I iterate through the array once, storing complements in the hash map.",
            "question": "Explain how to solve the two-sum problem.",
            "question_type": "technical",
            "expected": "high"
        },
        {
            "response": "Um, I'm not really sure about this problem. Maybe you just try all combinations?",
            "question": "Explain how to solve the two-sum problem.",
            "question_type": "technical",
            "expected": "low"
        },
        {
            "response": "When I faced a conflict with a team member, I scheduled a private conversation to understand their perspective. I listened actively, acknowledged their concerns, and we worked together to find a solution that addressed both our viewpoints. This improved our working relationship significantly.",
            "question": "Tell me about a time you resolved a conflict.",
            "question_type": "behavioral",
            "expected": "high"
        },
        {
            "response": "I don't really like conflicts, so I usually just stay quiet when there are disagreements.",
            "question": "Tell me about a time you resolved a conflict.",
            "question_type": "behavioral",
            "expected": "low"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        score = trainer.predict_score(
            test["response"],
            test["question"],
            test["question_type"]
        )
        
        rating = 'Excellent' if score > 0.8 else 'Good' if score > 0.6 else 'Average' if score > 0.4 else 'Poor'
        
        print(f"\n🧪 Test Case {i}:")
        print(f"   Question: {test['question']}")
        print(f"   Response: {test['response'][:80]}...")
        print(f"   Expected: {test['expected']} score")
        print(f"   Predicted Score: {score:.3f} ({rating})")
        
        # Check if prediction aligns with expectation
        is_correct = (test['expected'] == 'high' and score > 0.6) or (test['expected'] == 'low' and score <= 0.6)
        print(f"   Prediction: {'✅ Correct' if is_correct else '❌ Incorrect'}")
    
    print("\n" + "=" * 60)
    print("🎉 Model training completed successfully!")
    print("   Model saved to: models/interview_classifier.pkl")
    print("   Ready to start the backend server!")

if __name__ == "__main__":
    main()