# MSU Maintenance System Deployment Guide

## Table of Contents
1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Database Setup](#database-setup)
5. [Application Deployment](#application-deployment)
6. [Monitoring and Logging](#monitoring-and-logging)
7. [Backup and Recovery](#backup-and-recovery)
8. [Troubleshooting](#troubleshooting)

## Overview

The MSU Maintenance System is a comprehensive web application for managing maintenance operations at MSU. This guide covers the complete deployment process from development to production environments.

### Architecture

- **Frontend**: Flask web application with Bootstrap 5
- **Backend**: Python Flask with SQLAlchemy ORM
- **Database**: Microsoft SQL Server
- **Cache**: Redis for caching and session storage
- **Task Queue**: Celery with Redis broker
- **Web Server**: Gunicorn with Nginx reverse proxy
- **Containerization**: Docker and Kubernetes
- **CI/CD**: GitHub Actions

### Environments

- **Development**: Local development with Docker Compose
- **Staging**: Pre-production environment for testing
- **Production**: Live production environment

## Prerequisites

### System Requirements

- **CPU**: Minimum 2 cores, Recommended 4+ cores
- **Memory**: Minimum 4GB RAM, Recommended 8GB+ RAM
- **Storage**: Minimum 50GB, Recommended 100GB+ SSD
- **Network**: Stable internet connection

### Software Dependencies

- **Docker**: Version 20.10+
- **Docker Compose**: Version 2.0+
- **Kubernetes**: Version 1.24+ (for production)
- **SQL Server**: Version 2019+
- **Redis**: Version 7+
- **Python**: Version 3.9+
- **Node.js**: Version 16+ (for frontend tools)

### Required Accounts

- **Docker Hub**: For container registry access
- **Kubernetes Cluster**: For production deployment
- **AWS/Azure/GCP**: For cloud services (optional)
- **Email Service**: For notifications (optional)

## Environment Setup

### Development Environment

1. **Clone the Repository**
   ```bash
   git clone https://github.com/msu/maintenance-system.git
   cd maintenance-system
   ```

2. **Set Up Environment Variables**
   ```bash
   cp .env.development .env
   # Edit .env with your local configuration
   ```

3. **Start Services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Run Database Migrations**
   ```bash
   docker-compose exec web python scripts/migrate_database.py
   ```

5. **Create Admin User**
   ```bash
   docker-compose exec web python create_admin_user.py
   ```

6. **Access the Application**
   - Web App: http://localhost:5000
   - Flower (Celery Monitor): http://localhost:5555

### Staging Environment

1. **Set Up Kubernetes Cluster**
   ```bash
   # Configure kubectl for your staging cluster
   kubectl config use-context staging-cluster
   ```

2. **Create Namespace**
   ```bash
   kubectl apply -f k8s/namespace.yaml
   ```

3. **Configure Secrets**
   ```bash
   # Update k8s/config-secrets.yaml with actual values
   kubectl apply -f k8s/config-secrets.yaml
   ```

4. **Deploy Applications**
   ```bash
   kubectl apply -f k8s/redis-deployment.yaml
   kubectl apply -f k8s/web-deployment.yaml
   kubectl apply -f k8s/celery-worker-deployment.yaml
   kubectl apply -f k8s/celery-beat-deployment.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

5. **Verify Deployment**
   ```bash
   kubectl get pods -n msu-maintenance
   kubectl get services -n msu-maintenance
   kubectl get ingress -n msu-maintenance
   ```

### Production Environment

Follow the same steps as staging, but with production-specific configurations:

1. **Use Production Namespace**
   ```bash
   kubectl config use-context production-cluster
   ```

2. **Configure Production Secrets**
   - Use strong, unique passwords
   - Configure SSL certificates
   - Set up monitoring and alerting

3. **Enable High Availability**
   - Configure multiple replicas
   - Set up load balancing
   - Configure auto-scaling

## Database Setup

### SQL Server Installation

1. **Install SQL Server**
   ```bash
   # For Ubuntu/Debian
   wget -qO- https://packages.microsoft.com/keys/microsoft.ascendant | sudo apt-key add -
   sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/20.04/mssql-server-2019.list)"
   sudo apt-get update
   sudo apt-get install -y mssql-server
   ```

2. **Configure SQL Server**
   ```bash
   sudo /opt/mssql/bin/mssql-conf setup
   # Accept license terms and set SA password
   ```

3. **Enable SQL Server Authentication**
   ```bash
   sudo /opt/mssql/bin/mssql-conf set sql.enabled 1
   sudo systemctl restart mssql-server
   ```

### Database Creation

1. **Create Database**
   ```sql
   CREATE DATABASE CentralServices_AM_DB;
   GO
   ```

2. **Create Application User**
   ```sql
   -- Run the migration script
   :r database_migrations/009_create_app_user.sql
   ```

3. **Run Migrations**
   ```bash
   # Using the migration script
   ./scripts/migrate_database.sh
   ```

### Database Backup Configuration

1. **Set Up Backup Jobs**
   ```bash
   # Add to cron for daily backups
   0 2 * * * /path/to/scripts/backup_database.sh
   ```

2. **Configure Backup Retention**
   ```bash
   # Set retention policy in backup script
   RETENTION_DAYS=30
   ```

## Application Deployment

### Docker Deployment

1. **Build Docker Image**
   ```bash
   docker build -t msu-maintenance:latest .
   ```

2. **Run Container**
   ```bash
   docker run -d \
     --name msu-maintenance \
     -p 5000:5000 \
     --env-file .env \
     msu-maintenance:latest
   ```

### Docker Compose Deployment

1. **Production Compose File**
   ```yaml
   version: '3.8'
   services:
     web:
       image: msu-maintenance:latest
       restart: always
       environment:
         - ENV=production
       ports:
         - "5000:5000"
   ```

2. **Deploy with Compose**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### Kubernetes Deployment

1. **Build and Push Image**
   ```bash
   docker build -t your-registry/msu-maintenance:latest .
   docker push your-registry/msu-maintenance:latest
   ```

2. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f k8s/
   ```

3. **Monitor Deployment**
   ```bash
   kubectl get pods -n msu-maintenance -w
   ```

### Load Balancer Configuration

1. **Nginx Configuration**
   ```nginx
   upstream app_servers {
       server web1:5000;
       server web2:5000;
       server web3:5000;
   }
   ```

2. **SSL/TLS Setup**
   ```bash
   # Generate SSL certificates
   certbot --nginx -d maintenance.msu.ac.zw
   ```

## Monitoring and Logging

### Application Monitoring

1. **Health Checks**
   ```bash
   curl http://localhost:5000/health
   ```

2. **Performance Metrics**
   ```bash
   curl http://localhost:5000/api/v1/performance/metrics
   ```

3. **Application Logs**
   ```bash
   docker-compose logs -f web
   ```

### Database Monitoring

1. **SQL Server Monitoring**
   ```sql
   SELECT 
       session_id,
       login_name,
       status,
       cpu_time,
       memory_usage,
       total_elapsed_time
   FROM sys.dm_exec_sessions
   WHERE is_user_process = 1;
   ```

2. **Performance Counters**
   ```sql
   SELECT 
       counter_name,
       cntr_value
   FROM sys.dm_os_performance_counters
   WHERE counter_name LIKE '%Memory%';
   ```

### Infrastructure Monitoring

1. **Prometheus Setup**
   ```yaml
   global:
     scrape_interval: 15s
   scrape_configs:
     - job_name: 'msu-maintenance'
       static_configs:
         - targets: ['localhost:5000']
   ```

2. **Grafana Dashboard**
   - Application response time
   - Database performance
   - System resource usage
   - Error rates

### Alerting

1. **Configure Alerts**
   ```yaml
   groups:
   - name: msu-maintenance
     rules:
     - alert: HighErrorRate
       expr: error_rate > 0.05
       for: 5m
       annotations:
         summary: "High error rate detected"
   ```

2. **Notification Channels**
   - Email alerts
   - Slack notifications
   - PagerDuty integration

## Backup and Recovery

### Database Backup

1. **Full Backup**
   ```bash
   ./scripts/backup_database.sh --type=FULL
   ```

2. **Differential Backup**
   ```bash
   ./scripts/backup_database.sh --type=DIFFERENTIAL
   ```

3. **Transaction Log Backup**
   ```bash
   ./scripts/backup_database.sh --type=LOG
   ```

### Application Backup

1. **Code Repository Backup**
   ```bash
   git push origin main
   ```

2. **Configuration Backup**
   ```bash
   tar -czf config-backup-$(date +%Y%m%d).tar.gz .env* nginx/ k8s/
   ```

### Disaster Recovery

1. **Database Recovery**
   ```sql
   RESTORE DATABASE CentralServices_AM_DB 
   FROM DISK = '/path/to/backup/file'
   WITH NORECOVERY;
   ```

2. **Application Recovery**
   ```bash
   # Restore from git
   git checkout main
   git pull origin main
   
   # Redeploy
   kubectl apply -f k8s/
   ```

### Recovery Testing

1. **Test Backup Integrity**
   ```bash
   ./scripts/verify_backup.sh --backup-file=/path/to/backup
   ```

2. **Test Recovery Procedures**
   ```bash
   ./scripts/test_disaster_recovery.sh
   ```

## Troubleshooting

### Common Issues

#### Database Connection Issues

1. **Check Connection String**
   ```bash
   sqlcmd -S $DB_SERVER -U $DB_USER -P $DB_PASSWORD -Q "SELECT 1"
   ```

2. **Check Firewall**
   ```bash
   telnet $DB_SERVER 1433
   ```

3. **Check SQL Server Service**
   ```bash
   sudo systemctl status mssql-server
   ```

#### Application Issues

1. **Check Application Logs**
   ```bash
   docker-compose logs web
   ```

2. **Check Environment Variables**
   ```bash
   docker-compose exec web env | grep DB_
   ```

3. **Check Dependencies**
   ```bash
   docker-compose exec web pip list
   ```

#### Performance Issues

1. **Check System Resources**
   ```bash
   top
   df -h
   free -m
   ```

2. **Check Database Performance**
   ```sql
   SELECT 
       total_elapsed_time/1000 AS total_seconds,
       total_elapsed_time/execution_count/1000 AS avg_seconds,
       execution_count
   FROM sys.dm_exec_query_stats
   ORDER BY total_elapsed_time DESC;
   ```

3. **Check Application Performance**
   ```bash
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/
   ```

### Emergency Procedures

#### Application Down

1. **Check Service Status**
   ```bash
   kubectl get pods -n msu-maintenance
   ```

2. **Restart Services**
   ```bash
   kubectl rollout restart deployment/msu-maintenance-web -n msu-maintenance
   ```

3. **Check Logs**
   ```bash
   kubectl logs -f deployment/msu-maintenance-web -n msu-maintenance
   ```

#### Database Issues

1. **Check Database Status**
   ```sql
   SELECT state_desc FROM sys.databases WHERE name = 'CentralServices_AM_DB';
   ```

2. **Restart SQL Server**
   ```bash
   sudo systemctl restart mssql-server
   ```

3. **Check Disk Space**
   ```bash
   df -h /var/opt/mssql
   ```

#### Security Issues

1. **Check Failed Login Attempts**
   ```sql
   SELECT 
       login_name,
       login_type,
       attempt_time
   FROM sys.dm_exec_sessions
   WHERE is_user_process = 1;
   ```

2. **Review Security Logs**
   ```bash
   sudo journalctl -u mssql-server | grep -i error
   ```

### Performance Tuning

#### Database Optimization

1. **Update Statistics**
   ```sql
   EXEC sp_updatestats;
   ```

2. **Rebuild Indexes**
   ```sql
   EXEC sp_MSforeachtable 'EXEC sp_rebuild_index ''?'';
   ```

3. **Check Query Plans**
   ```sql
   SET SHOWPLAN_TEXT ON;
   GO
   SELECT * FROM job_requests WHERE status = 'PENDING';
   GO
   ```

#### Application Optimization

1. **Enable Caching**
   ```bash
   # Check Redis status
   redis-cli ping
   ```

2. **Monitor Response Times**
   ```bash
   curl -w "@curl-format.txt" -o /dev/null -s http://localhost:5000/api/v1/jobs
   ```

3. **Optimize Database Queries**
   ```bash
   # Enable slow query logging
   sqlcmd -S $DB_SERVER -U $DB_USER -P $DB_PASSWORD -Q "
   EXEC sp_configure 'show advanced options', 1;
   RECONFIGURE;
   EXEC sp_configure 'slow query threshold', 1000;
   RECONFIGURE;
   "
   ```

## Security Considerations

### Network Security

1. **Firewall Configuration**
   ```bash
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **SSL/TLS Configuration**
   ```bash
   # Generate self-signed certificate for testing
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365
   ```

### Application Security

1. **Environment Variables**
   - Never commit secrets to version control
   - Use strong, unique passwords
   - Rotate secrets regularly

2. **Access Control**
   - Implement least privilege principle
   - Use role-based access control
   - Regular access reviews

### Monitoring Security

1. **Security Scanning**
   ```bash
   # Run Bandit security scan
   bandit -r app/
   
   # Run OWASP ZAP scan
   python scripts/zap_security_scan.py --target http://localhost:5000
   ```

2. **Log Monitoring**
   - Monitor for suspicious activity
   - Set up alerting for security events
   - Regular security audits

## Maintenance Tasks

### Daily Tasks

- Check application health status
- Review error logs
- Monitor system resource usage
- Verify backup completion

### Weekly Tasks

- Apply security updates
- Review performance metrics
- Clean up old log files
- Test backup restoration

### Monthly Tasks

- Update dependencies
- Review access logs
- Perform security audit
- Update documentation

### Quarterly Tasks

- Disaster recovery testing
- Performance optimization
- Security assessment
- Capacity planning

## Support Contacts

### Technical Support

- **Application Issues**: development-team@msu.ac.zw
- **Database Issues**: dba-team@msu.ac.zw
- **Infrastructure Issues**: infrastructure-team@msu.ac.zw

### Emergency Contacts

- **Production Issues**: +263-XXX-XXXXXXX (24/7)
- **Security Issues**: security-team@msu.ac.zw

### Documentation

- **API Documentation**: https://docs.maintenance.msu.ac.zw
- **User Guide**: https://guide.maintenance.msu.ac.zw
- **GitHub Repository**: https://github.com/msu/maintenance-system

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-01-01 | Initial release |
| 1.1.0 | 2024-02-15 | Added notifications |
| 1.2.0 | 2024-03-01 | Performance improvements |
| 1.3.0 | 2024-04-01 | Security enhancements |

---

This deployment guide provides comprehensive instructions for deploying and maintaining the MSU Maintenance System. For additional support, please contact the technical team.
