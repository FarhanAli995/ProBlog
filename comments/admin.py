from django.contrib import admin
from .models import Comment, Report


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'blog', 'is_approved', 'is_reply', 'created_at']
    list_filter = ['is_approved', 'created_at']
    search_fields = ['user__username', 'content', 'blog__title']
    list_editable = ['is_approved']
    raw_id_fields = ['user', 'blog', 'parent']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reason', 'status', 'comment', 'blog', 'created_at']
    list_filter = ['status', 'reason', 'created_at']
    search_fields = ['reporter__username', 'details']
    list_editable = ['status']
    raw_id_fields = ['reporter', 'comment', 'blog', 'reviewed_by']
