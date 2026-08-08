from django.contrib import admin
from .models import Like, Bookmark, Follow


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog', 'created_at']
    raw_id_fields = ['user', 'blog']

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog', 'created_at']
    raw_id_fields = ['user', 'blog']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['follower', 'following', 'created_at']
    raw_id_fields = ['follower', 'following']
