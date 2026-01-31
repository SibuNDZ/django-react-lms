# Deployment Guide

This guide covers deploying the Django React LMS application to production.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment Options](#cloud-deployment-options)
5. [Environment Variables](#environment-variables)
6. [Database Management](#database-management)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker and Docker Compose (v2.0+)
- Python 3.11+ (for local development)
- Node.js 20+ (for local development)
- PostgreSQL 15+ (or use Docker)
- Redis 7+ (or use Docker)

---

## Local Development Setup

### Option 1: Docker Compose (Recommended)

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down
```

Access:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/swagger/

### Option 2: Manual Setup

**Backend:**
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run server
python manage.py runserver
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Docker Deployment

### Production Build

1. **Create environment file:**
   ```bash
   cp .env.production.example .env
   # Edit .env with production values
   ```

2. **Generate SSL certificates** (required for HTTPS):
   ```bash
   mkdir -p nginx/ssl
   # Option A: Use Let's Encrypt with certbot
   # Option B: Copy your existing certificates
   cp /path/to/fullchain.pem nginx/ssl/
   cp /path/to/privkey.pem nginx/ssl/
   ```

3. **Build and deploy:**
   ```bash
   # Build images
   docker-compose -f docker-compose.prod.yml build

   # Start services
   docker-compose -f docker-compose.prod.yml up -d

   # Run migrations
   docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate

   # Create superuser
   docker-compose -f docker-compose.prod.yml exec backend python manage.py createsuperuser

   # Collect static files (if not using S3)
   docker-compose -f docker-compose.prod.yml exec backend python manage.py collectstatic --noinput
   ```

4. **Verify deployment:**
   ```bash
   # Check health
   curl https://yourdomain.com/health/
   curl https://yourdomain.com/health/ready/

   # View logs
   docker-compose -f docker-compose.prod.yml logs -f
   ```

### SSL with Let's Encrypt

For automated SSL with Let's Encrypt, use certbot:

```bash
# Install certbot
apt-get install certbot

# Get certificate (standalone mode - stop nginx first)
docker-compose -f docker-compose.prod.yml stop nginx
certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# Copy certificates
cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/yourdomain.com/privkey.pem nginx/ssl/

# Restart nginx
docker-compose -f docker-compose.prod.yml start nginx
```

Set up auto-renewal:
```bash
# Add to crontab
0 0 * * * certbot renew --quiet && docker-compose -f /path/to/docker-compose.prod.yml restart nginx
```

---

## Cloud Deployment Options

### AWS ECS

1. **Push images to ECR:**
   ```bash
   # Authenticate
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com

   # Tag and push
   docker tag lms-backend:latest <account>.dkr.ecr.us-east-1.amazonaws.com/lms-backend:latest
   docker push <account>.dkr.ecr.us-east-1.amazonaws.com/lms-backend:latest
   ```

2. **Create ECS task definitions** for backend, frontend, celery worker, and celery beat

3. **Use managed services:**
   - RDS PostgreSQL for database
   - ElastiCache Redis for cache/broker
   - S3 for media storage
   - ALB for load balancing
   - ACM for SSL certificates

### DigitalOcean App Platform

1. Connect your GitHub repository
2. Configure environment variables in the App Platform dashboard
3. Use managed PostgreSQL and Redis add-ons
4. Configure the app spec:

```yaml
name: lms
services:
  - name: backend
    source:
      repo: your-repo
      branch: main
      source_dir: backend
    http_port: 8000
    instance_size: basic-xxs
    run_command: gunicorn backend.wsgi:application --bind 0.0.0.0:8000
    envs:
      - key: DATABASE_URL
        scope: RUN_TIME
        value: ${db.DATABASE_URL}

  - name: frontend
    source:
      repo: your-repo
      branch: main
      source_dir: frontend
    build_command: npm run build
    static:
      path: /dist
```

### Railway

1. Connect GitHub repository
2. Add PostgreSQL and Redis plugins
3. Configure environment variables
4. Deploy automatically on push

### Render

Create `render.yaml`:
```yaml
services:
  - type: web
    name: lms-backend
    env: docker
    dockerfilePath: ./backend/Dockerfile
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: lms-db
          property: connectionString

  - type: web
    name: lms-frontend
    env: static
    buildCommand: npm run build
    staticPublishPath: ./dist
    pullRequestPreviewsEnabled: true

databases:
  - name: lms-db
    plan: starter
```

---

## Environment Variables

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Django secret key | `django-insecure-...` |
| `POSTGRES_PASSWORD` | Database password | `strong-password` |
| `ALLOWED_HOSTS` | Allowed hostnames | `yourdomain.com,www.yourdomain.com` |

### Optional Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Debug mode | `False` |
| `DATABASE_URL` | Database connection URL | SQLite |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379/0` |
| `USE_S3` | Use S3 for media | `False` |
| `STRIPE_SECRET_KEY` | Stripe API key | - |
| `PAYPAL_CLIENT_ID` | PayPal client ID | - |
| `MAILGUN_API_KEY` | Mailgun API key | - |

### Frontend Build Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | API base URL |
| `VITE_STRIPE_PUBLIC_KEY` | Stripe publishable key |
| `VITE_PAYPAL_CLIENT_ID` | PayPal client ID |

---

## Database Management

### Migrations

```bash
# Create migrations
docker-compose exec backend python manage.py makemigrations

# Apply migrations
docker-compose exec backend python manage.py migrate

# Show migration status
docker-compose exec backend python manage.py showmigrations
```

### Backup & Restore

**Backup:**
```bash
# Create backup
docker-compose exec db pg_dump -U postgres lms_db > backup_$(date +%Y%m%d).sql

# Compress
gzip backup_$(date +%Y%m%d).sql
```

**Restore:**
```bash
# Restore from backup
gunzip backup_20240101.sql.gz
docker-compose exec -T db psql -U postgres lms_db < backup_20240101.sql
```

**Automated backups:**
```bash
# Add to crontab (daily at 2 AM)
0 2 * * * docker-compose -f /path/to/docker-compose.prod.yml exec -T db pg_dump -U postgres lms_db | gzip > /backups/lms_$(date +\%Y\%m\%d).sql.gz
```

---

## Monitoring & Logging

### Health Checks

| Endpoint | Purpose |
|----------|---------|
| `/health/` | Basic liveness check |
| `/health/ready/` | Readiness check (DB, Redis) |
| `/health/detailed/` | Detailed status with latencies |

### Log Access

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Recommended Monitoring Stack

1. **Error Tracking:** Sentry
   ```python
   # settings.py
   import sentry_sdk
   sentry_sdk.init(dsn=env("SENTRY_DSN"))
   ```

2. **APM:** Datadog or New Relic

3. **Metrics:** Prometheus + Grafana
   - Export Django metrics with django-prometheus
   - Monitor Redis with redis-exporter
   - Monitor PostgreSQL with postgres-exporter

4. **Log Aggregation:** ELK Stack or Loki

---

## Troubleshooting

### Common Issues

**1. Database connection refused**
```bash
# Check if PostgreSQL is running
docker-compose ps db

# Check logs
docker-compose logs db

# Verify connection
docker-compose exec db psql -U postgres -c "SELECT 1"
```

**2. Redis connection issues**
```bash
# Check if Redis is running
docker-compose exec redis redis-cli ping
```

**3. Static files not loading**
```bash
# Collect static files
docker-compose exec backend python manage.py collectstatic --noinput

# Check nginx configuration
docker-compose exec nginx nginx -t
```

**4. Celery tasks not processing**
```bash
# Check Celery worker
docker-compose logs celery_worker

# Verify broker connection
docker-compose exec celery_worker celery -A backend inspect ping
```

**5. CORS errors**
- Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
- Check that `ALLOWED_HOSTS` includes your domain

**6. 502 Bad Gateway**
- Check if backend container is healthy: `docker-compose ps`
- Review backend logs: `docker-compose logs backend`
- Verify nginx upstream configuration

### Performance Tuning

**Gunicorn workers:**
```dockerfile
# In Dockerfile CMD or docker-compose command
gunicorn --workers $((2 * $(nproc) + 1)) --threads 2 ...
```

**PostgreSQL:**
```sql
-- Increase connections
ALTER SYSTEM SET max_connections = 200;
-- Tune memory
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

**Redis:**
```
maxmemory 512mb
maxmemory-policy allkeys-lru
```

---

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` (use `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- [ ] HTTPS enabled with valid SSL certificate
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] `CORS_ALLOWED_ORIGINS` restricted to your domains
- [ ] Database credentials are strong and not committed to git
- [ ] `.env` file is in `.gitignore`
- [ ] Regular backups configured
- [ ] Rate limiting enabled
- [ ] Security headers configured in nginx
- [ ] Dependencies updated regularly (run `safety check` and `npm audit`)

---

## Support

For issues and feature requests, please open an issue on the GitHub repository.
