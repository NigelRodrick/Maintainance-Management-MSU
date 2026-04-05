# MSU Maintenance System - Rollback Strategy

## Overview
This document outlines the rollback strategy for the MSU Maintenance System deployment.

## Rollback Scenarios

### 1. Docker Image Rollback
**Trigger:** Health check fails or critical errors detected within 60 seconds of deployment

**Commands:**
```bash
# Get previous stable image tag
PREVIOUS_SHA=$(git describe --tags --abbrev=0 HEAD~1)

# Rollback to previous image
docker compose set image msu-maintenance=ghcr.io/maintenance/msu-maintenance:${PREVIOUS_SHA}

# Restart services
docker compose up -d --no-deps

# Verify rollback
docker compose ps
```

### 2. Database Migration Rollback
**Trigger:** Database integrity issues or data corruption detected

**Commands:**
```bash
# Rollback last migration
flask db downgrade

# Rollback to specific migration
flask db downgrade <migration_id>

# Verify database status
flask db current
```

### 3. Complete System Rollback
**Trigger:** Multiple component failures or system-wide issues

**Commands:**
```bash
# Stop current deployment
docker compose down

# Switch to previous stable branch
git checkout previous-stable

# Deploy previous version
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d

# Verify system health
curl -f http://localhost:5000/health
```

## Automated Rollback

### Health Check Monitoring
- Health endpoint: `/api/v1/health`
- Monitoring interval: 30 seconds
- Failure threshold: 3 consecutive failures
- Auto-rollback trigger: 60 seconds after deployment

### Rollback Script
```bash
#!/bin/bash
# rollback.sh - Automated rollback script

set -e

echo "🔄 Starting rollback procedure..."

# Get current deployment info
CURRENT_IMAGE=$(docker compose images -q msu-maintenance)
PREVIOUS_SHA=$(git describe --tags --abbrev=0 HEAD~1)

echo "Current image: $CURRENT_IMAGE"
echo "Rolling back to: $PREVIOUS_SHA"

# Stop current services
echo "⏹️ Stopping current services..."
docker compose down

# Rollback Docker image
echo "🔄 Rolling back Docker image..."
docker compose set image msu-maintenance=ghcr.io/maintenance/msu-maintenance:${PREVIOUS_SHA}

# Start services with rollback image
echo "▶️ Starting services with rollback image..."
docker compose up -d --no-deps

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Health check
echo "🏥 Running health check..."
if curl -f http://localhost:5000/health; then
    echo "✅ Rollback successful - System is healthy"
else
    echo "❌ Rollback failed - System is unhealthy"
    exit 1
fi

echo "🎉 Rollback completed successfully"
```

## Manual Rollback Procedures

### Emergency Rollback
1. **Immediate Actions:**
   - Stop all services: `docker compose down`
   - Notify stakeholders
   - Assess impact

2. **Rollback Steps:**
   - Identify last stable deployment
   - Switch to previous stable branch
   - Deploy previous version
   - Verify system functionality

3. **Post-Rollback:**
   - Monitor system health
   - Run smoke tests
   - Document rollback reasons
   - Plan fixes

### Communication Plan
- **Immediate:** Alert on Slack #deployments
- **Within 15 minutes:** Email to all stakeholders
- **Within 30 minutes:** Detailed incident report
- **Post-resolution:** Root cause analysis

## Rollback Testing

### Test Rollback Procedure
1. Deploy to staging environment
2. Intentionally introduce a failure
3. Execute rollback procedure
4. Verify rollback success
5. Document lessons learned

### Rollback Verification Checklist
- [ ] Services are running
- [ ] Health check passes
- [ ] Database connectivity works
- [ ] Authentication functions
- [ ] Critical workflows work
- [ ] No data corruption
- [ ] Performance is acceptable

## Contact Information
- **DevOps Team:** devops@msu.ac.zw
- **System Admin:** admin@msu.ac.zw
- **Emergency Contact:** +263-123-4567
