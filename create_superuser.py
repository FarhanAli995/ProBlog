#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'problog.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser if it doesn't exist
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='alyyfarhan4@gmail.com',
        password='admin321@#$'
    )
    print('✅ Superuser "admin" created successfully')
else:
    print('⚠️  Superuser "admin" already exists')

# Create editor user if it doesn't exist
if not User.objects.filter(username='alyyfarhan4').exists():
    editor = User.objects.create_user(
        username='alyyfarhan4',
        email='alyyfarhan4@gmail.com',
        password='aly321@#$',
        is_staff=True,
        is_superuser=True
    )
    print('✅ Editor user "alyyfarhan4" created successfully')
else:
    print('⚠️  Editor user "alyyfarhan4" already exists')
