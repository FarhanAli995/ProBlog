from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Mark a user as email verified'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to verify')
        parser.add_argument('--superuser', action='store_true', help='Verify all superusers')

    def handle(self, *args, **options):
        if options['superuser']:
            users = User.objects.filter(is_superuser=True)
            if not users.exists():
                self.stdout.write(self.style.ERROR('No superusers found'))
                return
            for user in users:
                profile, created = Profile.objects.get_or_create(user=user)
                profile.is_email_verified = True
                profile.save()
                self.stdout.write(self.style.SUCCESS(f'Verified superuser: {user.username}'))
            return

        username = options['username']
        try:
            user = User.objects.get(username=username)
            profile, created = Profile.objects.get_or_create(user=user)
            profile.is_email_verified = True
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'User {username} is now email verified'))
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User {username} not found'))
