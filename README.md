# ProBlog

ProBlog is a Django-based blogging platform with support for:

- user registration, login, and profile management
- role-based dashboards for authors, editors, moderators, and superusers
- blog posts with images and video uploads
- comments, likes, bookmarks, and reports
- dashboard analytics powered by Chart.js

## Setup

1. Create and activate a Python virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Apply migrations:

```powershell
python manage.py migrate
```

4. Create a superuser:

```powershell
python manage.py createsuperuser
```

5. Run the development server:

```powershell
python manage.py runserver
```

6. Open the site at:

```text
http://127.0.0.1:8000/
```

## Features

- Multi-role dashboard experience:
  - authors manage drafts and published posts
  - editors review and publish pending posts
  - moderators handle reports and hidden comments
  - superusers see site-wide analytics
- Blog media support with image and video uploads
- Dynamic charts for views, status distribution, and engagement
- Bookmark and like actions for authenticated users
- Email-enabled password reset and account management

## Run with Docker

You can run the whole project in Docker instead of setting up a local Python environment.

### Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose) installed and running.

### 1. Build and start the container

From the `problog/` directory (the one with `manage.py` and `Dockerfile`):

```bash
docker compose up --build
```

This builds the image, applies database migrations, collects static files, and starts the dev server on port 8000. Your `db.sqlite3` and `media/` folder are bind-mounted, so data persists on your machine across container restarts.

### 2. Open the site

```text
http://localhost:8000/
```

### 3. Create a superuser (first time only)

In a second terminal, while the container is running:

```bash
docker compose exec web python manage.py createsuperuser
```

### 4. Stop the container

```bash
docker compose down
```

### Configuration

Copy `.env.example` to `.env` to override defaults such as `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS`. `docker-compose.yml` will pick up a `.env` file automatically if present.

## Verifying Docker Is Working Correctly

Use these checks, in order, to confirm Docker itself and the ProBlog container are healthy.

**1. Docker engine is installed and running**

```bash
docker --version
docker info
```
`docker info` should return engine details without a connection error. If it errors, start Docker Desktop first.

**2. Docker Compose is available**

```bash
docker compose version
```

**3. The image builds without errors**

```bash
docker compose build
```
This should end with no red error output and a successful layer build.

**4. The container starts and stays running**

```bash
docker compose up -d
docker compose ps
```
The `web` service should show state `running` (or `Up`), not `Restarting` or `Exited`.

**5. Check the logs for migration and server startup**

```bash
docker compose logs -f web
```
You should see `Applying database migrations...`, then `Watching for file changes with StatReloader`, and `Starting development server at http://0.0.0.0:8000/`. Press Ctrl+C to stop following logs (this does not stop the container).

**6. The app responds over HTTP**

```bash
curl -I http://localhost:8000/
```
Expect an HTTP response (e.g. `HTTP/1.1 200 OK` or a redirect), not a connection-refused error. You can also just open `http://localhost:8000/` in a browser.

**7. The container can reach the database and run management commands**

```bash
docker compose exec web python manage.py check
```
Should print `System check identified no issues`.

**8. Shut everything down cleanly**

```bash
docker compose down
```
Running `docker compose ps` afterward should show no `web` service listed.

If any step fails, `docker compose logs web` is the first place to look for the actual Python/Django traceback.

## Run with Docker

You can run the whole project in Docker instead of setting up a local Python environment.

### Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose) installed and running.

### 1. Build and start the container

From the `problog/` directory (the one with `manage.py` and `Dockerfile`):

```bash
docker compose up --build
```

This builds the image, applies database migrations, collects static files, and starts the dev server on port 8000. Your `db.sqlite3` and `media/` folder are bind-mounted, so data persists on your machine across container restarts.

### 2. Open the site

```text
http://localhost:8000/
```

### 3. Create a superuser (first time only)

In a second terminal, while the container is running:

```bash
docker compose exec web python manage.py createsuperuser
```

### 4. Stop the container

```bash
docker compose down
```

### Configuration

Copy `.env.example` to `.env` to override defaults such as `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, and `DJANGO_ALLOWED_HOSTS`. `docker-compose.yml` will pick up a `.env` file automatically if present.

## Verifying Docker Is Working Correctly

Use these checks, in order, to confirm Docker itself and the ProBlog container are healthy.

**1. Docker engine is installed and running**

```bash
docker --version
docker info
```
`docker info` should return engine details without a connection error. If it errors, start Docker Desktop first.

**2. Docker Compose is available**

```bash
docker compose version
```

**3. The image builds without errors**

```bash
docker compose build
```
This should end with no red error output and a successful layer build.

**4. The container starts and stays running**

```bash
docker compose up -d
docker compose ps
```
The `web` service should show state `running` (or `Up`), not `Restarting` or `Exited`.

**5. Check the logs for migration and server startup**

```bash
docker compose logs -f web
```
You should see `Applying database migrations...`, then `Watching for file changes with StatReloader`, and `Starting development server at http://0.0.0.0:8000/`. Press Ctrl+C to stop following logs (this does not stop the container).

**6. The app responds over HTTP**

```bash
curl -I http://localhost:8000/
```
Expect an HTTP response (e.g. `HTTP/1.1 200 OK` or a redirect), not a connection-refused error. You can also just open `http://localhost:8000/` in a browser.

**7. The container can reach the database and run management commands**

```bash
docker compose exec web python manage.py check
```
Should print `System check identified no issues`.

**8. Shut everything down cleanly**

```bash
docker compose down
```
Running `docker compose ps` afterward should show no `web` service listed.

If any step fails, `docker compose logs web` is the first place to look for the actual Python/Django traceback.

## Demo Video

A screen recording of the running project is included in the repository at `media/blogs/media/11.mp4`.

You can watch it directly from GitHub by downloading the MP4 file or viewing it locally with any browser or media player that supports MP4.

## Recent Updates

- Added video upload support in the blog post form so users can select and upload video files from their PC or laptop.
- Added video display support on the blog detail page so uploaded videos show inline with the post.
- Added file validation for MP4 and WebM with a 50MB upload limit.
- Added a README demo video reference for `media/blogs/media/11.mp4`.

## Notes

- This project assumes `DEBUG = True` for local development.
- If you see line ending warnings when adding files on Windows, set `core.autocrlf` appropriately:

```powershell
git config --global core.autocrlf true
```
