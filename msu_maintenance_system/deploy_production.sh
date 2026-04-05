#!/bin/bash
# Production Deployment Script

echo "Starting production deployment..."

# Pre-deployment checks
echo "Running pre-deployment checks..."
./pre_deployment_checks.sh

# Backup current system
echo "Backing up current system..."
./backup_production.sh

# Deploy new version
echo "Deploying new version..."
docker-compose -f docker-compose.prod.yml pull
docker-compose -f docker-compose.prod.yml up -d

# Post-deployment verification
echo "Running post-deployment verification..."
./post_deployment_checks.sh

# Monitor for issues
echo "Starting deployment monitoring..."
./monitor_deployment.sh

echo "Production deployment complete"
echo "System available at: https://maintenance.msu.ac.zw"
