from django.core.management.base import BaseCommand
from django.utils import timezone
from accounts.models import EmailVerificationToken


class Command(BaseCommand):
    help = 'Delete expired email verification tokens'

    def handle(self, *args, **options):
        expired_tokens = EmailVerificationToken.objects.filter(
            expires_at__lt=timezone.now(),
            is_used=False
        )
        
        count = expired_tokens.count()
        expired_tokens.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully deleted {count} expired verification tokens')
        )
