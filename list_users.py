import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'problog.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

print("All users:")
for user in User.objects.all():
    verified = getattr(user.profile, 'is_email_verified', False) if hasattr(user, 'profile') else False
    print(f"  {user.username} (superuser: {user.is_superuser}, email: {user.email}, verified: {verified})")
