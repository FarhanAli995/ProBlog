#!/usr/bin/env python
"""
Test script to diagnose email configuration issues.
Run: python test_email_fixed.py
"""

import os
import django
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'problog.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("EMAIL CONFIGURATION TEST")
print("=" * 60)
print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"EMAIL_HOST_PASSWORD: {'SET' if settings.EMAIL_HOST_PASSWORD else 'NOT SET'}")
print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
print("=" * 60)

try:
    print("\nAttempting to send test email...")
    send_mail(
        subject="ProBlog Test Email",
        message="This is a test email from ProBlog to verify email configuration.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.EMAIL_HOST_USER],
        fail_silently=False,
    )
    print("[SUCCESS] Email sent successfully!")
except Exception as e:
    print(f"[ERROR] Email failed: {str(e)}")
    print("\n--- Possible solutions ---")
    print("1. Generate a new Gmail App Password: Google Account > Security > App Passwords")
    print("2. Enable 2-Factor Authentication on your Gmail account")
    print("3. Update EMAIL_HOST_PASSWORD in .env with the new app password")
    print("4. Restart the Django server after making changes")
