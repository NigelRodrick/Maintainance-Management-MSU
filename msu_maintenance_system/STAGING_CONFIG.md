# Staging Environment Configuration

Environment Variables:
FLASK_ENV=staging
DB_SERVER=staging-db.msu.ac.zw
DB_NAME=CentralServices_AM_Staging
DEBUG=true
LOG_LEVEL=INFO

Services:
- Web Server: staging.msu.ac.zw
- Database: staging-db.msu.ac.zw
- Monitoring: staging-monitor.msu.ac.zw

Docker Compose Staging:
docker-compose -f docker-compose.staging.yml up -d

Health Check:
curl -f http://staging.msu.ac.zw/health
