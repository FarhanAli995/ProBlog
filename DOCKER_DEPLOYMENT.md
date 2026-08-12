# ProBlog Docker Deployment Guide

## Updated Changes for Docker

### 1. Environment Variables

All sensitive configuration is now managed through environment variables:

- `DJANGO_SECRET_KEY` - Django secret key
- `DJANGO_DEBUG` - Debug mode (set to False in production)
- `DJANGO_ALLOWED_HOSTS` - Comma-separated list of allowed hosts
- `EMAIL_HOST_USER` - Gmail username for SMTP
- `EMAIL_HOST_PASSWORD` - Gmail app password (keep secret!)
- `DEFAULT_FROM_EMAIL` - Default sender email

### 2. Files Updated

- **Dockerfile**: Added python-dotenv installation
- **docker-compose.yml**: Added all environment variables and env_file support
- **.env.docker**: Example environment file for Docker

### 3. Deployment Steps

#### Option A: Development with Docker

1. **Copy environment file:**
   ```bash
   cp .env.docker .env
   ```

2. **Build and run:**
   ```bash
   docker-compose up --build
   ```

3. **Access the site:**
   - Open http://localhost:8000

#### Option B: Production Deployment

1. **Update .env with production values:**
   ```bash
   # Edit .env file
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   EMAIL_HOST_PASSWORD=your-real-app-password
   ```

2. **Build for production:**
   ```bash
   docker-compose -f docker-compose.yml up --build -d
   ```

3. **Check logs:**
   ```bash
   docker-compose logs -f
   ```

4. **Stop containers:**
   ```bash
   docker-compose down
   ```

#### Option C: Rebuild after code changes

```bash
# Stop containers
docker-compose down

# Rebuild with new code
docker-compose up --build -d

# Or rebuild specific service
docker-compose up --build web
```

### 4. Verify Email Configuration

To test email in Docker:

```bash
# Access the container shell
docker-compose exec web bash

# Run the test script
python test_email_fixed.py
```

### 5. Common Docker Commands

| Command | Description |
|---------|-------------|
| `docker-compose up` | Start containers in foreground |
| `docker-compose up -d` | Start containers in background |
| `docker-compose down` | Stop and remove containers |
| `docker-compose logs` | View container logs |
| `docker-compose exec web bash` | Open shell in web container |
| `docker-compose exec web python manage.py migrate` | Run migrations |
| `docker-compose exec web python manage.py createsuperuser` | Create admin user |
| `docker-compose ps` | List running containers |

### 6. Troubleshooting

**Issue: Email not sending**
- Check EMAIL_HOST_PASSWORD in .env
- Verify Gmail app password is correct
- Check container logs: `docker-compose logs web`

**Issue: Static files not loading**
- Run: `docker-compose exec web python manage.py collectstatic --noinput`
- Check STATIC_ROOT and STATIC_URL settings

**Issue: Database migrations**
- Run: `docker-compose exec web python manage.py migrate`

**Issue: Permission errors**
- Ensure volumes are correctly mounted
- Check file permissions in the container

### 7. Security Notes

⚠️ **Important:**
- Never commit `.env` files to version control
- Use different passwords for development and production
- Always set `DJANGO_DEBUG=False` in production
- Use `DJANGO_SECRET_KEY` from environment, not default
- Regularly update Gmail app passwords
- Use HTTPS in production
