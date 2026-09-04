# Deployment Guide

## Production Deployment

### Prerequisites

- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- Domain with SSL certificate
- AI API keys (OpenAI or Anthropic)

## Environment Configuration

### Production .env

```env
# Application
ENVIRONMENT=production
DEBUG=false
APP_NAME=Interview Platform
API_PREFIX=/api

# Database
DATABASE_URL=postgresql://user:password@db:5432/interview_platform
DATABASE_URL_TEST=postgresql://user:password@db:5432/interview_platform_test

# Redis
REDIS_URL=redis://redis:6379/0

# Security - CHANGE THESE!
SECRET_KEY=<generate-strong-random-key-min-32-chars>
JWT_SECRET_KEY=<generate-different-strong-random-key>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Provider (choose one)
AI_PROVIDER=openai  # or anthropic
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Storage
STORAGE_PATH=/app/storage
MAX_FILE_SIZE_MB=10

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Admin
ADMIN_EMAIL=admin@yourdomain.com
ADMIN_PASSWORD=<change-this-strong-password>
```

## Docker Deployment

### Build Production Image

```bash
# Build image
docker build -f docker/Dockerfile -t interview-platform:latest .

# Test image
docker run --rm interview-platform:latest python -c "import app; print('OK')"
```

### Deploy with Docker Compose

```bash
# Start services
docker-compose up -d

# Check logs
docker-compose logs -f backend

# Run migrations
docker-compose exec backend alembic upgrade head

# Create admin user (if not auto-created)
docker-compose exec backend python -c "
from app.core.database import SessionLocal
from app.models import User, UserRole
from app.security.auth import get_password_hash

db = SessionLocal()
admin = User(
    email='admin@example.com',
    hashed_password=get_password_hash('your-admin-password'),
    full_name='Admin',
    role=UserRole.ADMIN
)
db.add(admin)
db.commit()
"

# Check health
curl http://localhost:8000/health
```

## Reverse Proxy (Nginx)

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    client_max_body_size 10M;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/interview-platform/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

## Database Setup

### PostgreSQL Configuration

```bash
# Create production database
sudo -u postgres psql
CREATE DATABASE interview_platform;
CREATE USER interview_user WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE interview_platform TO interview_user;
\q

# Run migrations
cd backend
alembic upgrade head

# Create indexes (if needed)
psql -d interview_platform -c "
CREATE INDEX CONCURRENTLY idx_interviews_user_status 
ON interviews(user_id, status);
"
```

### Database Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump interview_platform | gzip > backup_$DATE.sql.gz

# Automate with cron
0 2 * * * /path/to/backup.sh
```

## SSL/TLS Setup

### Let's Encrypt (Certbot)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d yourdomain.com

# Auto-renewal (already set up)
sudo systemctl status certbot.timer
```

## Monitoring & Logging

### Application Logging

```python
# Configure in app/core/config.py
LOG_LEVEL=INFO
LOG_FORMAT=json

# Logs location
/var/log/interview-platform/app.log
```

### Monitor with Prometheus

```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'interview-platform'
    static_configs:
      - targets: ['localhost:8000']
```

### Health Checks

```bash
# Add to monitoring
*/5 * * * * curl -f http://localhost:8000/health || alert
```

## Scaling

### Horizontal Scaling

```yaml
# docker-compose.yml for multiple backends
backend:
  image: interview-platform:latest
  deploy:
    replicas: 3
  
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  ports:
    - "80:80"
    - "443:443"
```

### Database Replication

```bash
# Master-slave setup for read scalability
# See PostgreSQL documentation
```

## Security Hardening

### Firewall Rules

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Secrets Management

```bash
# Use environment variables
# Never commit secrets to git
# Rotate keys regularly

# Example: AWS Secrets Manager
aws secretsmanager create-secret \
  --name interview-platform/prod/db-password \
  --secret-string "your-password"
```

### Rate Limiting

```python
# Already implemented in app
# Configure in .env
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

## Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild image
docker-compose build backend

# Run migrations
docker-compose exec backend alembic upgrade head

# Restart services
docker-compose restart backend
```

### Database Maintenance

```bash
# Vacuum and analyze
psql -d interview_platform -c "VACUUM ANALYZE;"

# Check table sizes
psql -d interview_platform -c "
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_catalog.pg_statio_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
"
```

## Troubleshooting

### Application Won't Start

```bash
# Check logs
docker-compose logs backend

# Check database connection
docker-compose exec backend python -c "
from app.core.database import engine
with engine.connect() as conn:
    print('Database OK')
"

# Check Redis
docker-compose exec backend python -c "
from app.core.redis import get_redis
r = get_redis()
print(r.ping())
"
```

### High Memory Usage

```bash
# Check container stats
docker stats

# Limit resources in docker-compose.yml
backend:
  deploy:
    resources:
      limits:
        memory: 2G
        cpus: '1.0'
```

### Slow Queries

```bash
# Enable query logging
# postgresql.conf
log_min_duration_statement = 1000

# Analyze slow queries
psql -d interview_platform -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"
```

## Rollback Procedure

```bash
# Rollback deployment
git checkout previous-commit
docker-compose build backend
docker-compose up -d backend

# Rollback database
alembic downgrade -1

# Verify
curl http://localhost:8000/health
```

## Disaster Recovery

### Backup Restoration

```bash
# Stop application
docker-compose stop backend

# Restore database
gunzip < backup_20260831_020000.sql.gz | psql interview_platform

# Restart application
docker-compose start backend
```

### High Availability Setup

```yaml
# Use load balancer
# Multiple backend replicas
# Database replication
# Redis Sentinel/Cluster
```

## Compliance

### GDPR Considerations

- User data deletion API implemented
- Data retention policies configurable
- Audit logs for data access
- Privacy policy disclosure

### Data Security

- Passwords hashed with bcrypt
- JWT tokens for authentication
- HTTPS enforced
- Private file storage
- Input validation
- SQL injection prevention

## Performance Optimization

### Database Indexes

```sql
CREATE INDEX idx_interviews_user_status ON interviews(user_id, status);
CREATE INDEX idx_questions_interview ON interview_questions(interview_id);
CREATE INDEX idx_resumes_user ON resumes(user_id);
```

### Caching Strategy

```python
# Redis caching for:
- Resume parsing results (1 hour)
- Job role data (24 hours)
- Interview blueprints (during active interview)
```

### CDN for Static Assets

```nginx
# Serve frontend assets via CDN
location /static {
    # Point to CDN
    add_header X-CDN "enabled";
}
```

## Cost Optimization

### AI API Usage

```python
# Implement request caching
# Use cheaper models for simple tasks
# Batch requests where possible
# Set token limits
```

### Database Optimization

```sql
# Archive old interviews
-- Move completed interviews > 1 year to archive table
```

## Support & Maintenance

### Regular Tasks

- [ ] Daily: Check application logs
- [ ] Daily: Monitor error rates
- [ ] Weekly: Review performance metrics
- [ ] Weekly: Check disk space
- [ ] Monthly: Update dependencies
- [ ] Monthly: Security audit
- [ ] Quarterly: Disaster recovery drill
- [ ] Yearly: SSL certificate renewal check
