from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_http_methods
from blogs.models import Blog
from django.contrib.auth.models import User
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """Simple health check endpoint to debug deployment issues."""
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_ok = True
    except Exception as e:
        db_ok = False
        db_error = str(e)
    
    return JsonResponse({
        "status": "ok" if db_ok else "error",
        "database": "connected" if db_ok else f"error: {db_error}",
        "debug": settings.DEBUG,
        "allowed_hosts": settings.ALLOWED_HOSTS,
    })


def about(request):
    """
    Display the About ProBlog page with information about the platform,
    its mission, how it works, and the team.
    """
    # Get some dynamic statistics
    published_blogs = Blog.objects.filter(status=Blog.STATUS_PUBLISHED).count()
    total_authors = User.objects.filter(
        groups__name__in=['Authors', 'Editors']
    ).distinct().count()
    
    context = {
        'published_blogs': published_blogs,
        'total_authors': total_authors,
    }
    return render(request, 'pages/about.html', context)


@require_http_methods(["GET", "POST"])
def contact(request):
    """
    Display the Contact page and handle contact form submissions.
    Only authenticated users can send messages using their registered email.
    """
    # Require user to be logged in
    if not request.user.is_authenticated:
        messages.error(request, 'Please log in to send a message.')
        return render(request, 'pages/contact.html')
    
    if request.method == 'POST':
        # Use authenticated user's information (read-only, cannot be changed)
        name = request.user.get_full_name() or request.user.username
        email = request.user.email
        subject_line = request.POST.get('subject', '').strip()
        message_text = request.POST.get('message', '').strip()
        
        # Validation
        errors = []
        if not subject_line:
            errors.append('Subject is required.')
        if not message_text:
            errors.append('Message is required.')
        if not email:
            errors.append('Your account does not have an email address. Please update your profile.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'pages/contact.html')
        
        # Send email to administrator
        try:
            send_mail(
                subject=f"[ProBlog Contact] {subject_line}",
                message=f"From: {name} ({email})\n\nMessage:\n{message_text}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
            messages.success(request, 'Thank you! Your message has been sent successfully. We will get back to you soon.')
        except Exception as e:
            # Log internally for debugging
            logger.error(f"Contact form email error: {str(e)}")
            messages.error(request, 'There was an error sending your message. Please try again later.')
        
        # Redirect to prevent duplicate form submission on page refresh (PRG pattern)
        return redirect('pages:contact')
    
    return render(request, 'pages/contact.html')
