# Railway Deployment Guide

This guide walks you through deploying the Django React LMS to Railway.

## Prerequisites

1. A [Railway account](https://railway.app/) (free tier available)
2. GitHub repository with your code
3. Railway CLI (optional, for local management)

---

## Step 1: Create a New Project on Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Connect your GitHub account and select this repository

---

## Step 2: Add Database Services

### PostgreSQL
1. In your Railway project, click **"New"** → **"Database"** → **"PostgreSQL"**
2. Railway automatically provisions a PostgreSQL database
3. The `DATABASE_URL` will be automatically available

### Redis
1. Click **"New"** → **"Database"** → **"Redis"**
2. Railway provisions a Redis instance
3. The `REDIS_URL` will be automatically available

---

## Step 3: Deploy the Backend

1. Click **"New"** → **"GitHub Repo"**
2. Select this repository
3. Set the **Root Directory** to `backend`
4. Railway will detect the Dockerfile and build automatically

### Configure Environment Variables

Go to **Variables** tab and add:

```
SECRET_KEY=your-super-secret-key-generate-a-new-one
DEBUG=False
ALLOWED_HOSTS=your-app.railway.app
FRONTEND_SITE_URL=https://your-frontend.railway.app
USE_REDIS_CACHE=True

# Email (choose one)
MAILGUN_API_KEY=your-mailgun-api-key
MAILGUN_SENDER_DOMAIN=mg.yourdomain.com
FROM_EMAIL=noreply@yourdomain.com

# Payments
STRIPE_SECRET_KEY=sk_live_...
PAYPAL_CLIENT_ID=your-paypal-client-id
PAYPAL_SECRET_ID=your-paypal-secret-id

# Optional: S3 for media files
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
```

### Reference Database Variables

Click **"Add Reference"** and link:
- `DATABASE_URL` → from PostgreSQL service
- `REDIS_URL` → from Redis service

### Generate a Secret Key

Run this locally to generate a secure secret key:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## Step 4: Deploy the Frontend

1. Click **"New"** → **"GitHub Repo"**
2. Select this repository again
3. Set the **Root Directory** to `frontend`

### Configure Build Settings

Railway will use nixpacks. Add these environment variables:

```
VITE_API_URL=https://your-backend.railway.app/api
VITE_STRIPE_PUBLIC_KEY=pk_live_...
VITE_PAYPAL_CLIENT_ID=your-paypal-client-id
```

---

## Step 5: Deploy Celery Worker (Optional)

For background tasks (emails, etc.):

1. Click **"New"** → **"GitHub Repo"**
2. Select this repository
3. Set **Root Directory** to `backend`
4. Go to **Settings** → **Deploy** → **Custom Start Command**:
   ```
   celery -A backend worker --loglevel=info --concurrency=2
   ```
5. Add the same environment variables as the backend
6. Reference `DATABASE_URL` and `REDIS_URL`

---

## Step 6: Configure Networking

### Backend
1. Go to backend service → **Settings** → **Networking**
2. Click **"Generate Domain"** to get a public URL
3. Note the URL (e.g., `lms-backend.railway.app`)

### Frontend
1. Go to frontend service → **Settings** → **Networking**
2. Click **"Generate Domain"**
3. Note the URL (e.g., `lms-frontend.railway.app`)

### Custom Domain (Optional)
1. Click **"Add Custom Domain"**
2. Add your domain (e.g., `lms.yourdomain.com`)
3. Update your DNS with the provided CNAME record

---

## Step 7: Update CORS Settings

After deployment, update the backend's `CORS_ALLOWED_ORIGINS`:

```
CORS_ALLOWED_ORIGINS=https://lms-frontend.railway.app,https://lms.yourdomain.com
```

---

## Step 8: Run Migrations & Create Superuser

### Option A: Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to project
railway link

# Run migration
railway run -s backend python manage.py migrate

# Create superuser
railway run -s backend python manage.py createsuperuser
```

### Option B: Railway Shell (Web)
1. Go to backend service
2. Click **"Shell"** tab
3. Run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

---

## Environment Variables Reference

### Backend (Required)
| Variable | Description |
|----------|-------------|
| `SECRET_KEY` | Django secret key |
| `DATABASE_URL` | PostgreSQL connection (auto from Railway) |
| `REDIS_URL` | Redis connection (auto from Railway) |
| `ALLOWED_HOSTS` | Your Railway domain |
| `FRONTEND_SITE_URL` | Frontend URL for redirects |

### Backend (Optional)
| Variable | Description |
|----------|-------------|
| `DEBUG` | Set to `False` for production |
| `USE_REDIS_CACHE` | Enable Redis caching |
| `STRIPE_SECRET_KEY` | Stripe API key |
| `PAYPAL_CLIENT_ID` | PayPal client ID |
| `MAILGUN_API_KEY` | Mailgun for emails |

### Frontend
| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL |
| `VITE_STRIPE_PUBLIC_KEY` | Stripe publishable key |
| `VITE_PAYPAL_CLIENT_ID` | PayPal client ID |

---

## Monitoring & Logs

### View Logs
1. Go to any service
2. Click **"Logs"** tab
3. View real-time application logs

### Health Checks
Your backend exposes:
- `/health/` - Basic liveness
- `/health/ready/` - Readiness (DB, Redis)

---

## Troubleshooting

### Build Fails
- Check **Build Logs** for errors
- Ensure `requirements.txt` or `package.json` has no issues

### Database Connection Error
- Verify `DATABASE_URL` is linked correctly
- Check PostgreSQL service is running

### Static Files Not Loading
- Whitenoise is configured to serve static files
- Run `python manage.py collectstatic` if needed

### CORS Errors
- Update `CORS_ALLOWED_ORIGINS` to include frontend URL
- Ensure no trailing slashes in URLs

### 502 Bad Gateway
- Check if the service is healthy in logs
- Verify `PORT` environment variable is used (Railway sets this)

---

## Cost Estimation

Railway's free tier includes:
- $5 of usage credits/month
- Enough for small apps

For production:
- Starter plan: ~$5-10/month for this stack
- Pro plan: More resources, $20+/month

---

## Useful Commands

```bash
# Railway CLI
railway login          # Login to Railway
railway link           # Link to project
railway up             # Deploy current directory
railway logs           # View logs
railway run <cmd>      # Run command in service
railway shell          # Open shell in service
```

---

## Next Steps After Deployment

1. ✅ Test all endpoints at `https://your-backend.railway.app/swagger/`
2. ✅ Create admin account via `createsuperuser`
3. ✅ Configure payment providers (Stripe/PayPal)
4. ✅ Set up email provider (Mailgun)
5. ✅ Add custom domain (optional)
6. ✅ Enable monitoring/alerting
