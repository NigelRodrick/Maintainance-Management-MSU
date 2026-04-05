#!/bin/bash
# Staging Deployment Script

echo "Starting staging deployment..."

# Pre-deployment checks
echo "Running pre-deployment checks..."

# Build Docker image
echo "Building Docker image..."
docker build -t msu-maintenance:staging .

# Tag for registry
echo "Tagging image for registry..."
docker tag msu-maintenance:staging ghcr.io/maintenance/msu-maintenance:staging

# Deploy to staging
echo "Deploying to staging environment..."
docker-compose -f docker-compose.staging.yml up -d

# Health check
echo "Running health check..."
sleep 30
if curl -f http://staging.msu.ac.zw/health; then
    echo "Staging deployment successful"
else
    echo "Staging deployment failed"
    exit 1
fi

echo "Staging deployment complete"
