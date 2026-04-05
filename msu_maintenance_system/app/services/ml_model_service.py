"""
ML Model Service - MSU Maintenance System
Serves trained machine learning models for predictions
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MLModelService:
    """Machine Learning Model Service"""
    
    def __init__(self):
        self.models = {}
        self.model_dir = Path('models')
        self.model_dir.mkdir(exist_ok=True)
        self._load_models()
    
    def _load_models(self):
        """Load all trained models"""
        try:
            # Model 1: Priority Classifier
            priority_model_path = self.model_dir / 'priority_classifier_v1.pkl'
            if priority_model_path.exists():
                self.models['priority_classifier'] = joblib.load(priority_model_path)
                logger.info("Priority classifier loaded")
            
            # Model 2: Resolution Time Estimator
            time_model_path = self.model_dir / 'resolution_time_estimator_v1.pkl'
            if time_model_path.exists():
                self.models['resolution_time_estimator'] = joblib.load(time_model_path)
                logger.info("Resolution time estimator loaded")
            
            # Model 3: Technician Matcher
            matcher_model_path = self.model_dir / 'technician_matcher_v1.pkl'
            if matcher_model_path.exists():
                self.models['technician_matcher'] = joblib.load(matcher_model_path)
                logger.info("Technician matcher loaded")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def predict_priority(self, features: Dict) -> Dict:
        """Predict job priority using Random Forest model"""
        if 'priority_classifier' not in self.models:
            return {'error': 'Priority classifier not available'}
        
        try:
            # Prepare features
            feature_vector = self._prepare_priority_features(features)
            
            # Make prediction
            model = self.models['priority_classifier']
            prediction = model.predict([feature_vector])[0]
            probabilities = model.predict_proba([feature_vector])[0]
            
            return {
                'predicted_priority': int(prediction),
                'confidence': float(max(probabilities)),
                'probabilities': {
                    'low': float(probabilities[0]),
                    'medium': float(probabilities[1]),
                    'high': float(probabilities[2]),
                    'urgent': float(probabilities[3])
                },
                'model_version': 'v1',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Priority prediction error: {e}")
            return {'error': str(e)}
    
    def estimate_resolution_time(self, features: Dict) -> Dict:
        """Estimate resolution time using Gradient Boosting model"""
        if 'resolution_time_estimator' not in self.models:
            return {'error': 'Resolution time estimator not available'}
        
        try:
            # Prepare features
            feature_vector = self._prepare_time_features(features)
            
            # Make prediction
            model = self.models['resolution_time_estimator']
            prediction = model.predict([feature_vector])[0]
            
            return {
                'estimated_hours': float(max(0, prediction)),
                'estimated_days': float(max(0, prediction / 8)),
                'model_version': 'v1',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Resolution time estimation error: {e}")
            return {'error': str(e)}
    
    def recommend_technician(self, features: Dict) -> Dict:
        """Recommend technician using k-NN model"""
        if 'technician_matcher' not in self.models:
            return {'error': 'Technician matcher not available'}
        
        try:
            # Prepare features
            feature_vector = self._prepare_matcher_features(features)
            
            # Find nearest technicians
            model = self.models['technician_matcher']
            distances, indices = model.kneighbors([feature_vector], n_neighbors=5)
            
            # Get technician recommendations
            recommendations = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                recommendations.append({
                    'technician_id': int(idx),
                    'similarity_score': float(1 / (1 + dist)),
                    'rank': i + 1
                })
            
            return {
                'recommendations': recommendations,
                'model_version': 'v1',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Technician recommendation error: {e}")
            return {'error': str(e)}
    
    def _prepare_priority_features(self, features: Dict) -> List:
        """Prepare features for priority prediction"""
        # Feature engineering for priority classification
        return [
            features.get('category_id', 0),
            features.get('department_id', 0),
            len(features.get('description', '').split()),  # word count
            1 if 'urgent' in features.get('description', '').lower() else 0,
            1 if 'emergency' in features.get('description', '').lower() else 0,
            features.get('reported_by_role_level', 3),
            features.get('time_of_day', 12),  # hour of day
            features.get('day_of_week', 1),   # day of week
        ]
    
    def _prepare_time_features(self, features: Dict) -> List:
        """Prepare features for resolution time estimation"""
        return [
            features.get('priority', 2),
            features.get('category_id', 0),
            features.get('department_id', 0),
            features.get('technician_skill_level', 3),
            features.get('workload', 5),
            features.get('historical_avg_time', 4.0),
            features.get('material_count', 1),
            features.get('complexity_score', 3),
        ]
    
    def _prepare_matcher_features(self, features: Dict) -> List:
        """Prepare features for technician matching"""
        return [
            features.get('skill_category_match', 0.8),
            features.get('current_workload', 3),
            features.get('past_performance_score', 0.85),
            features.get('availability_score', 0.9),
            features.get('location_proximity', 0.7),
        ]
    
    def get_model_info(self) -> Dict:
        """Get information about loaded models"""
        return {
            'loaded_models': list(self.models.keys()),
            'model_directory': str(self.model_dir),
            'last_loaded': datetime.now().isoformat(),
            'available_models': {
                'priority_classifier': 'priority_classifier_v1.pkl' in [f.name for f in self.model_dir.glob('*.pkl')],
                'resolution_time_estimator': 'resolution_time_estimator_v1.pkl' in [f.name for f in self.model_dir.glob('*.pkl')],
                'technician_matcher': 'technician_matcher_v1.pkl' in [f.name for f in self.model_dir.glob('*.pkl')]
            }
        }
