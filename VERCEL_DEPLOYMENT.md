# ProBlog Vercel Deployment Guide

## ✅ Pre-Deployment Checklist

### Local Environment
- [ ] `python manage.py check` - No errors
- [ ] `python manage.py runserver` - Site works locally
- [ ] All migrations are applied
- [ ] `.env` file configured with local settings

### Database Setup
- [ ] **Option A**: Fresh start (empty PostgreSQL database)
- [ ] **Option B**: Export existing data
  ```bash
  python export_data.py
  # Creates data_export.json with all your data
  ```

### Code Ready
- [ ] All changes committed to GitHub
- [ ] `vercel.json` updated (no create_superuser in build)
- [ ] `settings.py` has DEBUG=False default
- [ ] Production security settings added

## 🚀 Vercel Deployment Steps

### 1. Create PostgreSQL Database (Neon)
1. Sign up at [Neon](https://neon.tech)
2. Create a new project
3. Get your connection string:
   ```
   postgresql://username:password@host/database?sslmode=require
   ```

### 2. Add Vercel Environment Variables

Go to Vercel Project → Settings → Environment Variables

| Variable | Value | Example |
|----------|-------|---------|
| `DJANGO_SECRET_KEY` | New random key | (generated) |
| `DJANGO_DEBUG` | `False` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `*.vercel.app,localhost` | `*.vercel.app,localhost` |
| `DATABASE_URL` | Neon connection string | `postgresql://...` |
| `EMAIL_HOST_USER` | Your Gmail | `alyyfarhan4@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Gmail App Password | (your app password) |
| `DEFAULT_FROM_EMAIL` | Your Gmail | `alyyfarhan4@gmail.com` |
| `PROD_SUPERUSER_USERNAME` | Admin username | `farhanbabu` |
| `PROD_SUPERUSER_EMAIL` | Admin email | `alyyfarhan4@gmail.com` |
| `PROD_SUPERUSER_PASSWORD` | Admin password | (secure password) |
| `CUSTOM_DOMAIN` | Your domain (optional) | `problog.com` |

### 3. Deploy
1. Push to GitHub: `git push origin main`
2. Vercel auto-deploys
3. Wait for deployment complete

### 4. Create Superuser on Production

After deployment, you have two options:

**Option A: Using the script**
```bash
# In Vercel Functions or through a one-time command
python create_production_superuser.py
```

**Option B: Using Django shell**
```bash
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> User = get_user_model()
>>> User.objects.create_superuser('farhanbabu', 'alyyfarhan4@gmail.com', 'your_password')
```

### 5. Load Existing Data (if migrating from SQLite)

If you exported data:
```bash
python manage.py loaddata data_export.json
```

## 🔧 Troubleshooting

### Database Connection Issues
- Check DATABASE_URL is correct
- Ensure PostgreSQL is accessible from Vercel
- Check Neon allowed IPs (should be public)

### Static Files Not Loading
- Run: `python manage.py collectstatic`
- Check `STATIC_ROOT` in settings
- Verify WhiteNoise middleware is enabled

### Email Verification Not Working
- Check Gmail App Password is valid
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Check less secure app access (use App Password)

### Migration Errors on Vercel
- Check migrations are committed to GitHub
- Run locally: `python manage.py makemigrations`
- Commit and push migration files

## 📊 Architecture

```
Local Development          Production
    ↓                        ↓
SQLite (db.sqlite3)      PostgreSQL (Neon)
    ↓                        ↓
Django (runserver)       Vercel (serverless)
    ↓                        ↓
/media/                  Cloudinary/R2 (future)
```

## 🔐 Security Notes

- **Never commit `.env` to GitHub**
- Use Vercel Environment Variables for secrets
- Keep `DJANGO_DEBUG=False` in production
- Use strong, unique passwords
- Enable 2FA on your Gmail account
- Rotate Gmail App Password periodically

## 📝 After Deployment

1. Test login with username/email
2. Test registration flow
3. Test email verification
4. Test password reset
5. Check dashboard and CRUD operations
6. Verify static files (CSS, JS, images)
7. Test media uploads (if supported)

## 🆘 Common Errors

### Error: "Database not found"
- Check DATABASE_URL environment variable
- Run migrations: `python manage.py migrate`

### Error: "Invalid CSRF token"
- Add your domain to CSRF_TRUSTED_ORIGINS
- Check DEBUG=False settings

### Error: "Email not sent"
- Verify Gmail App Password
- Check SMTP settings
- Check EMAIL_HOST_USER

### Error: "Permission denied"
- Check filesystem permissions
- Use Django's built-in permissions

## ✅ Success Indicators

- [ ] Site loads at `https://your-project.vercel.app`
- [ ] Can login with `farhanbabu` (or your superuser)
- [ ] Can register new users
- [ ] Email verification works
- [ ] Blog posts visible
- [ ] Comments work
- [ ] Dashboard accessible

---

**Need help?** Check the official docs:
- [Vercel Django Template](https://vercel.com/templates/backend/django-hello-world)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)
- [Neon PostgreSQL](https://neon.tech/docs/introduction)
