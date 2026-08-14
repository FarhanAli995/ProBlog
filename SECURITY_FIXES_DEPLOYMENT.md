# 🔒 Security Fixes Deployment Checklist

## Overview
This document summarizes all critical security fixes applied to the ProBlog project and provides step-by-step deployment instructions to ensure your production environment is secure.

**Date:** August 2026
**Status:** ✅ All fixes applied to codebase

---

## Issues Fixed

### 1. ✅ Hardcoded SECRET_KEY in settings.py
**Status:** Already using environment variable fallback  
**Action Required:** Set `DJANGO_SECRET_KEY` in production environment  
**Verification:** ✅ settings.py uses `os.environ.get('DJANGO_SECRET_KEY', fallback)`

### 2. ✅ DEBUG = True in Production
**Status:** Already using environment variable  
**Action Required:** Set `DJANGO_DEBUG=False` in production  
**Verification:** ✅ settings.py uses `os.environ.get('DJANGO_DEBUG', 'False') == 'True'`

### 3. ✅ ALLOWED_HOSTS Configuration
**Status:** FIXED - Now properly handles empty environment variable  
**Verification:** ✅ Added fallback to prevent 400 errors when DEBUG=False

### 4. ✅ SQLite in Production
**Status:** Already configured for PostgreSQL via DATABASE_URL  
**Action Required:** Set `DATABASE_URL` in production environment (not in code)  
**Verification:** ✅ settings.py uses `dj_database_url.config()`

### 5. ✅ Development Server (runserver) in Production
**Status:** FIXED - Docker now uses Gunicorn  
**Verification:** 
- ✅ Dockerfile CMD updated to Gunicorn
- ✅ docker-compose.yml command updated to Gunicorn
- ✅ Gunicorn in requirements.txt

### 6. ✅ Database Credentials Exposed in vercel.json
**Status:** FIXED - Removed DATABASE_URL from vercel.json  
**Action Required:** Add DATABASE_URL as a secret environment variable in Vercel Dashboard  
**Verification:** ✅ vercel.json no longer contains database credentials

### 7. ✅ STATIC_ROOT Configuration
**Status:** Already properly configured  
**Verification:** ✅ STATIC_ROOT and STATICFILES_STORAGE are set correctly

---

## 🚀 Deployment Steps

### For Vercel Deployment

#### 1. Rotate Database Password (CRITICAL)
Since the database password was exposed in vercel.json, you MUST rotate it:

1. Log in to your Neon Database Dashboard
2. Navigate to your database project
3. Go to Settings → Database Credentials
4. **Regenerate the password** for the `neondb_owner` user
5. Copy the new connection string with the new password

#### 2. Set Environment Variables in Vercel
1. Go to your Vercel project dashboard
2. Navigate to Settings → Environment Variables
3. Add/Update these variables:

| Variable | Value | Environment |
|----------|-------|-------------|
| `DJANGO_SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_urlsafe(50))"` | Production |
| `DATABASE_URL` | New connection string from Neon (with rotated password) | Production |
| `DJANGO_DEBUG` | `False` | Production |
| `DJANGO_ALLOWED_HOSTS` | `yourdomain.com,www.yourdomain.com,.vercel.app,.now.sh` | Production |
| `EMAIL_HOST_PASSWORD` | Your Gmail App Password | Production |
| `PROD_SUPERUSER_USERNAME` | Your admin username | Production |
| `PROD_SUPERUSER_EMAIL` | Your admin email | Production |
| `PROD_SUPERUSER_PASSWORD` | Your admin password | Production |
| `CUSTOM_DOMAIN` | Your custom domain (optional) | Production |

#### 3. Deploy to Vercel
```bash
# Commit all changes
git add .
git commit -m "Security fixes: removed exposed credentials, switched to Gunicorn, fixed ALLOWED_HOSTS"

# Push to deploy
git push origin main
```

#### 4. Verify Deployment
- Visit your site and ensure it loads correctly
- Check that static files load (CSS, JS)
- Test login functionality
- Verify database operations work

#### 5. Invalidate Old Sessions (Recommended)
After deploying with new SECRET_KEY:
```bash
# Connect to your production database and clear sessions
python manage.py shell -c "from django.contrib.sessions.models import Session; Session.objects.all().delete()"
```
This forces all users to log in again.

---

### For Docker Deployment

#### 1. Create .env File
Copy `.env.example` to `.env` and fill in production values:
```bash
cp .env.example .env
```

#### 2. Edit .env with Production Values
```bash
DJANGO_SECRET_KEY=your-generated-secret-key
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://username:password@host/database?sslmode=require
EMAIL_HOST_PASSWORD=your-gmail-app-password
```

#### 3. Rebuild and Deploy
```bash
docker compose down
docker compose up --build -d
```

#### 4. Create Superuser (if first deployment)
```bash
docker compose exec web python manage.py createsuperuser
```

#### 5. Verify
- Check logs: `docker compose logs web`
- Visit site and test functionality

---

## 🔧 Testing Checklist

Before deploying to production, test these locally:

### Local Testing with Production-like Settings
```bash
# Test with DEBUG=False
DJANGO_DEBUG=False python manage.py runserver

# Visit site and verify:
# - All pages load without 500 errors
# - Static files work
# - Login functionality works
# - Blog posts display correctly

# Test collectstatic
python manage.py collectstatic --noinput --clear

# Test migrations (if any)
python manage.py migrate --noinput
```

### Test Gunicorn Locally (Optional)
```bash
# Install gunicorn if not already installed
pip install gunicorn

# Run with gunicorn
gunicorn --bind 127.0.0.1:8000 --workers 2 problog.wsgi:application

# Visit http://127.0.0.1:8000/ in your browser
```

---

## 📋 Monitoring After Deployment

### Check These Within 24 Hours
- [ ] Site loads without errors
- [ ] No 400/500 errors in logs
- [ ] User authentication works
- [ ] Database operations work
- [ ] Email functionality works
- [ ] Static files load (CSS, JS, images)
- [ ] Video uploads work
- [ ] Dashboard analytics load

### Monitor Security
- [ ] Verify DEBUG=False by triggering an error (404 should not show stack trace)
- [ ] Check that environment variables are properly loaded
- [ ] Confirm ALLOWED_HOSTS is working by attempting to access with invalid host

---

## 🔄 Rollback Plan

If issues occur after deployment:

### For Vercel
1. Go to Vercel Dashboard → Deployments
2. Find the previous successful deployment
3. Click "Promote to Production"

### For Docker
```bash
# Stop current containers
docker compose down

# Revert to previous version (if using git tags)
git checkout previous-version-tag
docker compose up --build -d
```

---

## 📝 Additional Security Recommendations

### Future Enhancements
1. **Enable HSTS** - Already configured in settings.py (commented out). Uncomment after confirming domain works.
2. **Rate Limiting** - Add for login and API endpoints
3. **Security Headers** - Consider using `django-csp` or `django-security`
4. **Regular Security Audits** - Run `bandit -r problog/` periodically
5. **Dependency Updates** - Regularly run `pip list --outdated`
6. **Database Backups** - Set up automated daily backups

### Monitoring Tools
- **Sentry** - Error tracking
- **New Relic** - Performance monitoring
- **Uptime Robot** - Uptime monitoring
- **Vercel Analytics** - Built-in analytics

---

## ✅ Final Status

| Issue | Status | Fixed In |
|-------|--------|----------|
| SECRET_KEY exposed | ✅ Fixed | settings.py (env var) |
| DEBUG=True in prod | ✅ Fixed | settings.py (env var) |
| ALLOWED_HOSTS empty | ✅ Fixed | settings.py |
| SQLite in production | ✅ Fixed | settings.py (DATABASE_URL) |
| runserver in production | ✅ Fixed | Dockerfile, docker-compose.yml |
| Credentials in vercel.json | ✅ Fixed | vercel.json |
| Static files configuration | ✅ Fixed | settings.py |

---

## 📞 Support

If you encounter any issues during deployment:

1. Check logs:
   - Vercel: Go to your project → Deployments → Click a deployment → Logs
   - Docker: `docker compose logs web`

2. Common issues:
   - **400 Bad Request**: Check ALLOWED_HOSTS includes your domain
   - **Database connection errors**: Verify DATABASE_URL is correct and password is rotated
   - **Static files missing**: Run `python manage.py collectstatic --noinput`
   - **Email not working**: Check EMAIL_HOST_PASSWORD is correct Gmail App Password

3. Environment variables not loading:
   - Vercel: Confirm they're set in Environment Variables section
   - Docker: Check .env file exists and has correct format

---

## 🎯 Success Criteria

You're done when:
1. ✅ All code changes are committed
2. ✅ vercel.json no longer contains DATABASE_URL
3. ✅ Database password has been rotated
4. ✅ New DATABASE_URL set as secret environment variable
5. ✅ DJANGO_SECRET_KEY set as environment variable
6. ✅ Site loads correctly in production
7. ✅ No security warnings in Django admin

**Congratulations! Your ProBlog is now secure and production-ready! 🎉**
