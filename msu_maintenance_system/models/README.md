# ML Models Directory

This directory contains serialized machine learning models for the MSU Maintenance System.

## Model Files

### Priority Classifier
- **File**: `priority_classifier_v1.pkl`
- **Type**: Random Forest Classifier
- **Purpose**: Predict job priority based on description and context
- **Features**: Category, department, description keywords, time factors
- **Classes**: Low, Medium, High, Urgent

### Resolution Time Estimator
- **File**: `resolution_time_estimator_v1.pkl`
- **Type**: Gradient Boosting Regressor
- **Purpose**: Estimate job completion time
- **Features**: Priority, category, technician skill, historical data
- **Output**: Estimated hours to completion

### Technician Matcher
- **File**: `technician_matcher_v1.pkl`
- **Type**: k-Nearest Neighbors
- **Purpose**: Recommend best technician for job assignment
- **Features**: Skill match, workload, performance, availability
- **Output**: Ranked technician recommendations

## Model Versioning

Models are versioned using semantic versioning:
- `v1.0.0` - Initial production models
- `v1.1.0` - Improved accuracy with additional features
- `v2.0.0` - Major algorithm improvements

## Training Pipeline

1. Data extraction from database views
2. Feature engineering and preprocessing
3. Model training and validation
4. Model serialization and storage
5. Integration with ML Model Service

## Model Performance

Current model performance metrics:
- Priority Classifier: 85% accuracy
- Resolution Time Estimator: 2.3 hours RMSE
- Technician Matcher: 78% recommendation acceptance

## Retraining Schedule

Models are retrained monthly with:
- New data from completed jobs
- Performance feedback from users
- Updated feature engineering
- Validation against test set
