#!/usr/bin/env python
"""
Generate a secure Django secret key for production.
Use this to create a key for your Vercel environment variables.

Usage: python generate_secret_key.py
"""
from django.core.management.utils import get_random_secret_key

if __name__ == '__main__':
    key = get_random_secret_key()
    print("=" * 60)
    print("YOUR DJANGO SECRET KEY FOR PRODUCTION")
    print("=" * 60)
    print(key)
    print("=" * 60)
    print("\nAdd this as DJANGO_SECRET_KEY in Vercel Environment Variables")
