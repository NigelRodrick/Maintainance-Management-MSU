# Production Environment Configuration

Environment Variables:
FLASK_ENV=production
DB_SERVER=prod-db.msu.ac.zw
DB_NAME=CentralServices_AM_Production
DEBUG=false
LOG_LEVEL=WARNING

Services:
- Web Server: maintenance.msu.ac.zw
- Database: prod-db.msu.ac.zw
- Monitoring: prod-monitor.msu.ac.zw
- SSL: Enabled

Docker Compose Production:
docker-compose -f docker-compose.prod.yml up -d

Health Check:
curl -f https://maintenance.msu.ac.zw/health
