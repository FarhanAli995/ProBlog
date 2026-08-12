from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_verification_email(request, user, token):
    """Send email verification link to user"""
    try:
        current_site = get_current_site(request)
        verification_link = f"http://{current_site.domain}{reverse('accounts:verify_email', kwargs={'token': token})}"
        
        subject = 'Verify Your Email Address - ProBlog'
        html_message = render_to_string('accounts/email/verification_email.html', {
            'user': user,
            'verification_link': verification_link,
            'site_name': 'ProBlog',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Verification email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_password_reset_email(request, user, token, uidb64):
    """Send password reset email with verification"""
    try:
        current_site = get_current_site(request)
        reset_link = f"http://{current_site.domain}{reverse('accounts:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})}"
        
        subject = 'Reset Your Password - ProBlog'
        html_message = render_to_string('accounts/email/password_reset_email.html', {
            'user': user,
            'reset_link': reset_link,
            'site_name': 'ProBlog',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Password reset email sent to {user.email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False