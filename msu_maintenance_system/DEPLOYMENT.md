# MSU Maintenance System - Deployment Guide

## Overview
This guide provides step-by-step instructions for deploying the MSU Maintenance System to production.

## Prerequisites

### System Requirements
- **Operating System:** Ubuntu 20.04+ or CentOS 8+
- **Memory:** Minimum 4GB RAM, Recommended 8GB+
- **Storage:** Minimum 20GB free space
- **Network:** Stable internet connection
- **Database:** SQL Server 2019+ or MySQL 8.0+

### Software Requirements
- **Docker:** 20.10+
- **Docker Compose:** 2.0+
- **Git:** 2.30+
- **Python:** 3.11+ (for local development)

### Environment Variables
```bash
# Application Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=production

# Database Configuration
DB_SERVER=your-db-server
DB_NAME=CentralServices_AM_DB
DB_USER=your-db-user
DB_PASSWORD=your-db-password

# Optional: SSL Configuration
SSL_CERT_PATH=/path/to/cert.pem
SSL_KEY_PATH=/path/to/key.pem
```

## Deployment Methods

### Method 1: Docker Compose (Recommended)

#### Step 1: Prepare Environment
```bash
# Clone repository
git clone https://github.com/maintenance/msu-maintenance-system.git
cd msu-maintenance-system

# Create environment file
cp .env.example .env
# Edit .env with your actual values
```

#### Step 2: Deploy Application
```bash
# Pull latest images
docker compose -f docker-compose.prod.yml pull

# Start services
docker compose -f docker-compose.prod.yml up -d

# Verify deployment
docker compose -f docker-compose.prod.yml ps
```

#### Step 3: Health Check
```bash
# Check application health
curl -f http://localhost:5000/health

# Check logs
docker compose -f docker-compose.prod.yml logs -f web
```

### Method 2: Manual Deployment

#### Step 1: Prepare Server
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

#### Step 2: Deploy Application
```bash
# Create application directory
sudo mkdir -p /opt/msu-maintenance
cd /opt/msu-maintenance

# Clone repository
sudo git clone https://github.com/maintenance/msu-maintenance-system.git .

# Set permissions
sudo chown -R $USER:$USER /opt/msu-maintenance
```

#### Step 3: Configure and Start
```bash
# Create environment file
cp .env.example .env
# Edit .env with production values

# Start services
docker compose -f docker-compose.prod.yml up -d
```

## Post-Deployment Verification

### Health Checks
```bash
# Application health
curl -f http://localhost:5000/health

# Database connectivity
curl -f http://localhost:5000/api/v1/health/db

# Authentication test
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "test@staff.msu.ac.zw", "password": "test"}'
```

### Smoke Tests
```bash
# Run smoke tests
python phase3_smoke_tests_final.py

# Check critical functionality
curl -f http://localhost:5000/
curl -f http://localhost:5000/auth/login
curl -f http://localhost:5000/dashboard
```

## Monitoring and Maintenance

### Log Monitoring
```bash
# View application logs
docker compose -f docker-compose.prod.yml logs -f web

# View database logs
docker compose -f docker-compose.prod.yml logs -f db

# Rotate logs
docker compose -f docker-compose.prod.yml logs --tail=1000
```

### Performance Monitoring
```bash
# Check resource usage
docker stats

# Check disk usage
df -h

# Check memory usage
free -h
```

### Backup Procedures
```bash
# Database backup
docker compose exec db sqlcmd -S localhost -U sa -Q "BACKUP DATABASE CentralServices_AM_DB TO DISK='/backup/backup.bak'"

# Application backup
docker compose -f docker-compose.prod.yml down
tar -czf msu-maintenance-backup-$(date +%Y%m%d).tar.gz .
```

## Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
docker compose logs web

# Check environment variables
docker compose exec web env | grep -E "(SECRET_KEY|DB_)"

# Restart services
docker compose restart web
```

#### Database Connection Issues
```bash
# Test database connectivity
docker compose exec db sqlcmd -S localhost -U sa -Q "SELECT 1"

# Check database logs
docker compose logs db

# Restart database
docker compose restart db
```

#### Performance Issues
```bash
# Check resource usage
docker stats

# Scale web service
docker compose up -d --scale web=2

# Clear cache
docker compose exec web flask cache clear
```

### Emergency Procedures
1. **Immediate Response:**
   - Check system status
   - Identify affected services
   - Notify stakeholders

2. **Rollback if Needed:**
   - Execute rollback procedure
   - Verify system stability
   - Monitor for issues

3. **Post-Incident:**
   - Document root cause
   - Update procedures
   - Schedule review meeting

## Security Considerations

### SSL/TLS Configuration
```bash
# Configure SSL certificates
cp your-cert.pem /etc/ssl/certs/msu-maintenance.crt
cp your-key.pem /etc/ssl/private/msu-maintenance.key

# Update nginx configuration
# Add SSL configuration to nginx.conf
```

### Firewall Configuration
```bash
# Open required ports
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable
```

### Access Control
```bash
# Restrict access to admin panel
# Configure IP whitelisting
# Set up VPN access
```

## Support and Contacts

### Technical Support
- **DevOps Team:** devops@msu.ac.zw
- **System Admin:** admin@msu.ac.zw
- **Database Admin:** dba@msu.ac.zw

### Emergency Contacts
- **On-call Engineer:** +263-123-4567
- **IT Helpdesk:** +263-987-6543
- **Management:** +263-555-1234

### Documentation
- **API Documentation:** https://docs.msu-maintenance.ac.zw/api
- **User Guide:** https://docs.msu-maintenance.ac.zw/user-guide
- **Admin Guide:** https://docs.msu-maintenance.ac.zw/admin-guide

## Version Information
- **Current Version:** 1.0.0
- **Last Updated:** 2024-04-04
- **Next Release:** 1.1.0 (Planned for 2024-06-01)

## Change Log

### Version 1.0.0 (2024-04-04)
- Initial production release
- Complete CI/CD pipeline
- Comprehensive testing suite
- Security hardening
- Performance optimization

### Upcoming Features

### Version 1.1.0 (Planned)
- Mobile application support
- Advanced analytics dashboard
- Automated reporting
- Enhanced security features
