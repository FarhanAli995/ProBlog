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
