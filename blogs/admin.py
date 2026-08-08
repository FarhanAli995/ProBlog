from django.contrib import admin
from .models import Blog, Category, Tag, BlogReview


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'status', 'is_featured', 'views', 'created_at']
    list_filter = ['status', 'is_featured', 'category', 'created_at']
    search_fields = ['title', 'author__username', 'content']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['views', 'created_at', 'updated_at', 'published_at']
    list_editable = ['status', 'is_featured']
    date_hierarchy = 'created_at'
    filter_horizontal = ['tags']
    raw_id_fields = ['author', 'category']


@admin.register(BlogReview)
class BlogReviewAdmin(admin.ModelAdmin):
    list_display = ['blog', 'editor', 'decision', 'created_at']
    list_filter = ['decision', 'created_at']
    raw_id_fields = ['blog', 'editor']
