from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a verified superuser with username, email, and password'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username')
        parser.add_argument('email', type=str, help='Email address')
        parser.add_argument('password', type=str, help='Password')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User {username} already exists'))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        profile, created = Profile.objects.get_or_create(user=user)
        profile.is_email_verified = True
        profile.save()
        
        self.stdout.write(self.style.SUCCESS(f'Superuser {username} created and verified!'))
        self.stdout.write(f'Email: {email}')
        self.stdout.write(f'Password: {password}')
