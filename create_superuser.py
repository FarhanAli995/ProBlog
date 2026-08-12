#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'problog.settings')
django.setup()

from django.contrib.auth.models import User

# Create superuser if it doesn't exist
if not User.objects.filter(username='farhanali').exists():
    User.objects.create_superuser(
        username='farhanali',
        email='farhanaly812@gmail.com',
        password='FarhanAli@2024'
    )
    print('✅ Superuser "farhanali" created with email farhanaly812@gmail.com')
    print('   Password: FarhanAli@2024')
else:
    print('⚠️  Superuser "farhanali" already exists')

# Create admin user if it doesn't exist
if not User.objects.filter(username='admin').exists():
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@problog.com',
        password='AdminProBlog@2024'
    )
    print('✅ Admin user "admin" created')
    print('   Password: AdminProBlog@2024')
else:
    print('⚠️  Admin user "admin" already exists')
