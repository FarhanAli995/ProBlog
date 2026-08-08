from django.db import models
from django.conf import settings
from blogs.models import Blog


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes',
    )
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'blog'], name='unique_user_blog_like')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} liked "{self.blog.title}"'


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarks',
    )
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'blog'], name='unique_user_blog_bookmark')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user.username} bookmarked "{self.blog.title}"'


class Follow(models.Model):
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following',
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['follower', 'following'], name='unique_follow')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.follower.username} follows {self.following.username}'
