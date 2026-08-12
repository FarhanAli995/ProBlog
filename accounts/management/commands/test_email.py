from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Test email sending'

    def handle(self, *args, **options):
        # Force UTF-8 encoding for stdout
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8')
        
        self.stdout.write('Testing email configuration...')
        self.stdout.write(f'EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        
        try:
            send_mail(
                'Test Email from ProBlog',
                'This is a test email to verify the configuration is working.\n\nIf you received this, the email configuration is working correctly!',
                settings.DEFAULT_FROM_EMAIL,
                ['alyyfarhan4@gmail.com'],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS('SUCCESS: Test email sent successfully!'))
            self.stdout.write('Please check your Gmail inbox (and spam folder).')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR: Failed to send email: {str(e)}'))
