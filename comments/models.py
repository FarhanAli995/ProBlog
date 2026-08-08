from django.db import models
from django.conf import settings
from blogs.models import Blog


class Comment(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
    )
    content = models.TextField(max_length=1000)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment by {self.user.username} on "{self.blog.title}"'

    @property
    def is_reply(self):
        return self.parent is not None


class Report(models.Model):
    REASON_SPAM = 'SPAM'
    REASON_HATE = 'HATE'
    REASON_MISINFORMATION = 'MISINFORMATION'
    REASON_INAPPROPRIATE = 'INAPPROPRIATE'
    REASON_OTHER = 'OTHER'

    REASON_CHOICES = [
        (REASON_SPAM, 'Spam'),
        (REASON_HATE, 'Hate Speech'),
        (REASON_MISINFORMATION, 'Misinformation'),
        (REASON_INAPPROPRIATE, 'Inappropriate Content'),
        (REASON_OTHER, 'Other'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_REVIEWED = 'REVIEWED'
    STATUS_DISMISSED = 'DISMISSED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_REVIEWED, 'Reviewed'),
        (STATUS_DISMISSED, 'Dismissed'),
    ]

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reports_filed',
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports',
    )
    blog = models.ForeignKey(
        Blog,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='reports',
    )
    reason = models.CharField(max_length=20, choices=REASON_CHOICES)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_reviewed',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        target = f'Comment #{self.comment_id}' if self.comment else f'Blog "{self.blog}"'
        return f'Report on {target} by {self.reporter.username}'
