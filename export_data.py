#!/usr/bin/env python
"""
Export SQLite data to a JSON fixture for loading into PostgreSQL.
Run this locally before deploying to Vercel.

Usage: python export_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'problog.settings')
django.setup()

from django.core.management import call_command
from django.contrib.auth import get_user_model

User = get_user_model()

print("📦 Exporting data from SQLite to fixture...")

# Export all data except contenttypes and permissions (they auto-create)
exclude = ['contenttypes', 'auth.permission']

# Check if there's any data to export
user_count = User.objects.count()
if user_count == 0:
    print("⚠️  No users found in database. Nothing to export.")
    print("💡 If this is a fresh database, skip export and deploy with empty DB.")
    exit(0)

print(f"👤 Found {user_count} users to export")

# Export to fixture
call_command('dumpdata', 
    exclude=exclude,
    natural_foreign=True,
    natural_primary=True,
    indent=2,
    output='data_export.json'
)

print("✅ Data exported to data_export.json")
print("📋 Next steps:")
print("1. Deploy to Vercel (PostgreSQL will be empty)")
print("2. Run: python manage.py loaddata data_export.json")
print("3. Or use: heroku run python manage.py loaddata data_export.json")
