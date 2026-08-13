#!/usr/bin/env python
"""
Create a superuser on production using environment variables.
Run this once after deployment on Vercel.

Usage: python create_production_superuser.py

Environment variables needed:
PROD_SUPERUSER_USERNAME=admin
PROD_SUPERUSER_EMAIL=admin@example.com
PROD_SUPERUSER_PASSWORD=your_secure_password
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'problog.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()

def create_superuser():
    username = os.environ.get('PROD_SUPERUSER_USERNAME')
    email = os.environ.get('PROD_SUPERUSER_EMAIL')
    password = os.environ.get('PROD_SUPERUSER_PASSWORD')
    
    if not all([username, email, password]):
        print("❌ Missing environment variables.")
        print("Please set: PROD_SUPERUSER_USERNAME, PROD_SUPERUSER_EMAIL, PROD_SUPERUSER_PASSWORD")
        sys.exit(1)
    
    # Check if user exists
    if User.objects.filter(username=username).exists():
        print(f"⚠️  User '{username}' already exists. Skipping.")
        return
    
    # Create superuser
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    
    # Mark as verified
    profile, created = Profile.objects.get_or_create(user=user)
    profile.is_email_verified = True
    profile.save()
    
    print(f"✅ Superuser created successfully!")
    print(f"   Username: {username}")
    print(f"   Email: {email}")
    print("   Password: [hidden]")
    print("   Email verified: Yes")

if __name__ == '__main__':
    create_superuser()
