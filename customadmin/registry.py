"""
Declarative registry for the ProBlog custom admin.

Each AdminSection describes how one model is exposed in /admin/: which
columns show in the list view, which fields are searchable/filterable,
and which ModelForm powers add/edit. Views and templates read this
registry instead of hard-coding per-model logic.
"""

from django.contrib.auth.models import User, Group

from accounts.models import Profile
from blogs.models import Blog, Category, Tag, BlogReview
from comments.models import Comment, Report
from interactions.models import Like, Bookmark, Follow

from . import forms as admin_forms


class AdminSection:
    def __init__(self, *, slug, model, group, list_display, verbose_name=None,
                 verbose_name_plural=None, search_fields=None, list_filter=None,
                 form_class=None, can_add=True, can_edit=True, can_delete=True,
                 ordering=None):
        self.slug = slug
        self.model = model
        self.group = group
        self.verbose_name = verbose_name or model._meta.verbose_name.title()
        self.verbose_name_plural = verbose_name_plural or model._meta.verbose_name_plural.title()
        self.list_display = list_display
        self.search_fields = search_fields or []
        self.list_filter = list_filter or []
        self.form_class = form_class
        self.can_add = can_add and form_class is not None
        self.can_edit = can_edit and form_class is not None
        self.can_delete = can_delete
        self.ordering = ordering


REGISTRY = [
    AdminSection(
        slug='users', model=User, group='Authentication',
        verbose_name='User', verbose_name_plural='Users',
        list_display=[('username', 'Username'), ('email', 'Email'),
                       ('first_name', 'First name'), ('is_staff', 'Staff'),
                       ('is_superuser', 'Superuser'), ('is_active', 'Active'),
                       ('date_joined', 'Joined')],
        search_fields=['username', 'email', 'first_name', 'last_name'],
        list_filter=[('is_staff', 'Staff'), ('is_superuser', 'Superuser'), ('is_active', 'Active')],
        form_class=admin_forms.UserEditForm,
        ordering='-date_joined',
    ),
    AdminSection(
        slug='groups', model=Group, group='Authentication',
        verbose_name='Group', verbose_name_plural='Groups',
        list_display=[('name', 'Name')],
        search_fields=['name'],
        form_class=admin_forms.GroupForm,
        ordering='name',
    ),
    AdminSection(
        slug='profiles', model=Profile, group='Accounts',
        verbose_name='Profile', verbose_name_plural='Profiles',
        list_display=[('user', 'User'), ('location', 'Location'), ('created_at', 'Created')],
        search_fields=['user__username', 'user__email', 'location'],
        form_class=admin_forms.ProfileForm,
        can_add=False, can_delete=False,
        ordering='-created_at',
    ),
    AdminSection(
        slug='blogs', model=Blog, group='Blogs',
        verbose_name='Blog', verbose_name_plural='Blogs',
        list_display=[('title', 'Title'), ('author', 'Author'), ('category', 'Category'),
                       ('status', 'Status'), ('is_featured', 'Featured'),
                       ('views', 'Views'), ('created_at', 'Created')],
        search_fields=['title', 'author__username', 'content'],
        list_filter=[('status', 'Status'), ('is_featured', 'Featured')],
        form_class=admin_forms.BlogForm,
        ordering='-created_at',
    ),
    AdminSection(
        slug='categories', model=Category, group='Blogs',
        verbose_name='Category', verbose_name_plural='Categories',
        list_display=[('name', 'Name'), ('slug', 'Slug'), ('created_at', 'Created')],
        search_fields=['name'],
        form_class=admin_forms.CategoryForm,
        ordering='name',
    ),
    AdminSection(
        slug='tags', model=Tag, group='Blogs',
        verbose_name='Tag', verbose_name_plural='Tags',
        list_display=[('name', 'Name'), ('slug', 'Slug')],
        search_fields=['name'],
        form_class=admin_forms.TagForm,
        ordering='name',
    ),
    AdminSection(
        slug='blog-reviews', model=BlogReview, group='Blogs',
        verbose_name='Blog review', verbose_name_plural='Blog reviews',
        list_display=[('blog', 'Blog'), ('editor', 'Editor'),
                       ('decision', 'Decision'), ('created_at', 'Created')],
        search_fields=['blog__title', 'editor__username'],
        list_filter=[('decision', 'Decision')],
        form_class=admin_forms.BlogReviewForm,
        ordering='-created_at',
    ),
    AdminSection(
        slug='comments', model=Comment, group='Comments',
        verbose_name='Comment', verbose_name_plural='Comments',
        list_display=[('user', 'User'), ('blog', 'Blog'),
                       ('is_approved', 'Approved'), ('created_at', 'Created')],
        search_fields=['user__username', 'content', 'blog__title'],
        list_filter=[('is_approved', 'Approved')],
        form_class=admin_forms.CommentForm,
        can_add=False,
        ordering='-created_at',
    ),
    AdminSection(
        slug='reports', model=Report, group='Comments',
        verbose_name='Report', verbose_name_plural='Reports',
        list_display=[('reporter', 'Reporter'), ('reason', 'Reason'), ('status', 'Status'),
                       ('blog', 'Blog'), ('comment', 'Comment'), ('created_at', 'Created')],
        search_fields=['reporter__username', 'details'],
        list_filter=[('status', 'Status'), ('reason', 'Reason')],
        form_class=admin_forms.ReportForm,
        can_add=False,
        ordering='-created_at',
    ),
    AdminSection(
        slug='likes', model=Like, group='Interactions',
        verbose_name='Like', verbose_name_plural='Likes',
        list_display=[('user', 'User'), ('blog', 'Blog'), ('created_at', 'Created')],
        search_fields=['user__username', 'blog__title'],
        can_add=False, can_edit=False,
        ordering='-created_at',
    ),
    AdminSection(
        slug='bookmarks', model=Bookmark, group='Interactions',
        verbose_name='Bookmark', verbose_name_plural='Bookmarks',
        list_display=[('user', 'User'), ('blog', 'Blog'), ('created_at', 'Created')],
        search_fields=['user__username', 'blog__title'],
        can_add=False, can_edit=False,
        ordering='-created_at',
    ),
    AdminSection(
        slug='follows', model=Follow, group='Interactions',
        verbose_name='Follow', verbose_name_plural='Follows',
        list_display=[('follower', 'Follower'), ('following', 'Following'), ('created_at', 'Created')],
        search_fields=['follower__username', 'following__username'],
        can_add=False, can_edit=False,
        ordering='-created_at',
    ),
]

REGISTRY_BY_SLUG = {section.slug: section for section in REGISTRY}

_GROUP_ORDER = ['Authentication', 'Accounts', 'Blogs', 'Comments', 'Interactions']


def grouped_sections():
    """Sections bucketed by nav group, in a fixed display order."""
    buckets = {name: [] for name in _GROUP_ORDER}
    for section in REGISTRY:
        buckets.setdefault(section.group, []).append(section)
    return [(name, buckets[name]) for name in _GROUP_ORDER if buckets[name]]
