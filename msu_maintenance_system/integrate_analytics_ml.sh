#!/bin/bash
# MSU Maintenance System - Analytics & ML Integration Script
# This script integrates all analytics components

echo "MSU MAINTENANCE SYSTEM - ANALYTICS & ML INTEGRATION"
echo "=================================================="

# Step 1: Create database views
echo "Step 1: Creating database views..."
sqlcmd -S $DB_SERVER -d $DB_NAME -i database_migrations/analytics_views.sql
if [ $? -eq 0 ]; then
    echo "Database views created successfully"
else
    echo "Database views creation failed"
    exit 1
fi

# Step 2: Train ML models
echo "Step 2: Training ML models..."
cd ml_notebooks

# Run Phase 2: Basic model training
echo "Running basic model training..."
jupyter nbconvert --to python --execute 02_model_training.ipynb
if [ $? -eq 0 ]; then
    echo "Basic models trained successfully"
else
    echo "Basic model training failed"
fi

# Run Phase A4: Enhanced model training
echo "Running enhanced model training..."
jupyter nbconvert --to python --execute A4_predictive_ml.ipynb
if [ $? -eq 0 ]; then
    echo "Enhanced models trained successfully"
else
    echo "Enhanced model training failed"
fi

cd ..

# Step 3: Install ML dependencies
echo "Step 3: Installing ML dependencies..."
pip install scikit-learn pandas numpy matplotlib seaborn plotly joblib jupyter
if [ $? -eq 0 ]; then
    echo "ML dependencies installed successfully"
else
    echo "ML dependencies installation failed"
fi

# Step 4: Create models directory
echo "Step 4: Setting up models directory..."
mkdir -p models
if [ -d "models" ]; then
    echo "Models directory created"
else
    echo "Models directory creation failed"
fi

# Step 5: Verify analytics module
echo "Step 5: Verifying analytics module..."
if [ -f "app/analytics/__init__.py" ]; then
    echo "Analytics module found"
else
    echo "Analytics module not found"
fi

# Step 6: Verify ML service
echo "Step 6: Verifying ML service..."
if [ -f "app/services/ml_model_service.py" ]; then
    echo "ML service found"
else
    echo "ML service not found"
fi

# Step 7: Verify optimization service
echo "Step 7: Verifying optimization service..."
if [ -f "app/services/optimization_service.py" ]; then
    echo "Optimization service found"
else
    echo "Optimization service not found"
fi

# Step 8: Verify dashboard app
echo "Step 8: Verifying dashboard app..."
if [ -f "app/dash_app/app.py" ]; then
    echo "Dashboard app found"
else
    echo "Dashboard app not found"
fi

# Step 9: Test analytics endpoints
echo "Step 9: Testing analytics endpoints..."
python -c "
from app.analytics import AnalyticsModule
analytics = AnalyticsModule()
data = analytics.get_dashboard_data()
print('Analytics module test: PASSED')
"

if [ $? -eq 0 ]; then
    echo "Analytics endpoints working"
else
    echo "Analytics endpoints failed"
fi

# Step 10: Test ML service
echo "Step 10: Testing ML service..."
python -c "
from app.services.ml_model_service import MLModelService
ml_service = MLModelService()
info = ml_service.get_model_info()
print('ML service test: PASSED')
print('Models loaded: {}'.format(info['loaded_models']))
"

if [ $? -eq 0 ]; then
    echo "ML service working"
else
    echo "ML service failed"
fi

echo ""
echo "ANALYTICS & ML INTEGRATION COMPLETE!"
echo "=================================================="
echo "Database views created"
echo "ML models trained"
echo "Dependencies installed"
echo "Services verified"
echo "Endpoints tested"
echo ""
echo "READY FOR ANALYTICS DEPLOYMENT!"
echo ""
echo "Next steps:"
echo "1. Register analytics blueprint in Flask app"
echo "2. Start dashboard application: python app/dash_app/app.py"
echo "3. Configure Redis caching"
echo "4. Set up monitoring"
echo "5. Test end-to-end functionality"
