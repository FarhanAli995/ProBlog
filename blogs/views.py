from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.http import HttpResponseForbidden
from django.utils import timezone

from .models import Blog, Category, Tag, BlogReview
from .forms import BlogForm, CategoryForm, TagForm, ReviewForm


# ─── Helpers ───────────────────────────────────────────────────────────────────

def is_editor(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='Editors').exists()
    )

def is_author(user):
    return user.is_authenticated and (
        user.is_superuser or
        user.groups.filter(name__in=['Authors', 'Editors']).exists()
    )


# ─── Public Views ──────────────────────────────────────────────────────────────

def home(request):
    """Public homepage — list published blogs with search/filter/sort."""
    blogs_qs = Blog.objects.filter(status=Blog.STATUS_PUBLISHED).select_related(
        'author', 'category', 'author__profile'
    ).prefetch_related('tags')

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        blogs_qs = blogs_qs.filter(
            Q(title__icontains=q) |
            Q(excerpt__icontains=q) |
            Q(content__icontains=q) |
            Q(author__username__icontains=q) |
            Q(tags__name__icontains=q) |
            Q(category__name__icontains=q)
        ).distinct()

    # Filter by category
    category_slug = request.GET.get('category', '')
    if category_slug:
        blogs_qs = blogs_qs.filter(category__slug=category_slug)

    # Filter by tag
    tag_slug = request.GET.get('tag', '')
    if tag_slug:
        blogs_qs = blogs_qs.filter(tags__slug=tag_slug)

    # Sort
    sort = request.GET.get('sort', '-published_at')
    sort_map = {
        'newest': '-published_at',
        'oldest': 'published_at',
        'views': '-views',
        'featured': '-is_featured',
    }
    blogs_qs = blogs_qs.order_by(sort_map.get(sort, '-published_at'))

    # Pagination
    paginator = Paginator(blogs_qs, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    featured = Blog.objects.filter(
        status=Blog.STATUS_PUBLISHED, is_featured=True
    ).select_related('author', 'author__profile').first()

    context = {
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'featured': featured,
        'q': q,
        'current_category': category_slug,
        'current_tag': tag_slug,
        'current_sort': sort,
        'title': 'ProBlog — Latest Articles',
    }
    return render(request, 'blogs/home.html', context)


def blog_detail(request, slug):
    """Public blog detail page."""
    blog = get_object_or_404(Blog, slug=slug)

    # Only allow public access to published; owners/staff can view others
    if blog.status != Blog.STATUS_PUBLISHED:
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if blog.author != request.user and not is_editor(request.user):
            return HttpResponseForbidden()

    blog.increment_views()

    # Check user interactions
    user_liked = False
    user_bookmarked = False
    if request.user.is_authenticated:
        from interactions.models import Like, Bookmark
        user_liked = Like.objects.filter(user=request.user, blog=blog).exists()
        user_bookmarked = Bookmark.objects.filter(user=request.user, blog=blog).exists()

    from comments.models import Comment
    from comments.forms import CommentForm, ReplyForm
    top_comments = blog.comments.filter(parent=None, is_approved=True).select_related(
        'user', 'user__profile'
    ).prefetch_related('replies__user', 'replies__user__profile')

    comment_form = CommentForm()
    reply_form = ReplyForm()

    context = {
        'blog': blog,
        'top_comments': top_comments,
        'comment_form': comment_form,
        'reply_form': reply_form,
        'user_liked': user_liked,
        'user_bookmarked': user_bookmarked,
        'title': blog.title,
    }
    return render(request, 'blogs/blog_detail.html', context)


def category_list(request):
    categories = Category.objects.all()
    return render(request, 'blogs/category_list.html', {
        'categories': categories,
        'title': 'All Categories',
    })


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    blogs_qs = Blog.objects.filter(
        status=Blog.STATUS_PUBLISHED, category=category
    ).select_related('author', 'author__profile')
    paginator = Paginator(blogs_qs, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'blogs/category_detail.html', {
        'category': category,
        'page_obj': page_obj,
        'title': f'Category: {category.name}',
    })


def author_list(request):
    from django.contrib.auth.models import User
    authors = User.objects.filter(
        blogs__status=Blog.STATUS_PUBLISHED
    ).distinct().select_related('profile')
    return render(request, 'blogs/author_list.html', {
        'authors': authors,
        'title': 'All Authors',
    })


# ─── Author-Only Views ─────────────────────────────────────────────────────────

@login_required
def blog_create(request):
    if not (request.user.is_staff or is_author(request.user)):
        messages.error(request, 'You need author or staff permissions to create blog posts.')
        return redirect('blogs:home')

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES)
        if form.is_valid():
            blog = form.save(commit=False)
            blog.author = request.user
            blog.status = Blog.STATUS_DRAFT
            blog.save()
            form.save_m2m()
            messages.success(request, f'Draft "{blog.title}" created successfully!')
            return redirect('blogs:blog_detail', slug=blog.slug)
    else:
        form = BlogForm()

    return render(request, 'blogs/blog_create.html', {
        'form': form,
        'title': 'Create New Post',
        'action': 'Create',
    })


@login_required
def blog_edit(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    # Only author or editor/superuser can edit
    if blog.author != request.user and not is_editor(request.user):
        return HttpResponseForbidden()

    # Author can only edit DRAFT, REJECTED, CHANGES_REQUESTED
    if blog.author == request.user and blog.status not in (
        Blog.STATUS_DRAFT, Blog.STATUS_REJECTED, Blog.STATUS_CHANGES
    ) and not is_editor(request.user):
        messages.warning(request, 'You can only edit drafts or rejected/change-requested posts.')
        return redirect('blogs:blog_detail', slug=slug)

    if request.method == 'POST':
        form = BlogForm(request.POST, request.FILES, instance=blog)
        if form.is_valid():
            updated = form.save(commit=False)
            # If author re-submits changes, reset to draft
            if blog.author == request.user and blog.status in (
                Blog.STATUS_REJECTED, Blog.STATUS_CHANGES
            ):
                updated.status = Blog.STATUS_DRAFT
            updated.save()
            form.save_m2m()
            messages.success(request, f'Post "{blog.title}" updated!')
            return redirect('blogs:blog_detail', slug=blog.slug)
    else:
        form = BlogForm(instance=blog)

    return render(request, 'blogs/blog_form.html', {
        'form': form,
        'blog': blog,
        'title': f'Edit: {blog.title}',
        'action': 'Save Changes',
    })


@login_required
def blog_delete(request, slug):
    blog = get_object_or_404(Blog, slug=slug)

    if blog.author != request.user and not request.user.is_superuser:
        return HttpResponseForbidden()

    if request.method == 'POST':
        title = blog.title
        blog.delete()
        messages.success(request, f'Post "{title}" has been deleted.')
        return redirect('dashboard:author')

    return render(request, 'blogs/blog_delete.html', {'blog': blog})


@login_required
def blog_submit(request, slug):
    """Author submits draft for editorial review."""
    blog = get_object_or_404(Blog, slug=slug, author=request.user)

    if blog.status not in (Blog.STATUS_DRAFT, Blog.STATUS_REJECTED, Blog.STATUS_CHANGES):
        messages.warning(request, 'This post cannot be submitted right now.')
        return redirect('blogs:blog_detail', slug=slug)

    blog.status = Blog.STATUS_PENDING
    blog.save()
    messages.success(request, f'"{blog.title}" submitted for review!')
    return redirect('dashboard:author')


# ─── Editor Views ──────────────────────────────────────────────────────────────

@login_required
def review_blog(request, slug):
    """Editor reviews a pending blog post."""
    if not is_editor(request.user):
        return HttpResponseForbidden()

    blog = get_object_or_404(Blog, slug=slug, status=Blog.STATUS_PENDING)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            decision = form.cleaned_data['decision']
            feedback = form.cleaned_data['feedback']

            BlogReview.objects.create(
                blog=blog,
                editor=request.user,
                decision=decision,
                feedback=feedback,
            )

            if decision == 'APPROVED':
                blog.status = Blog.STATUS_PUBLISHED
                messages.success(request, f'"{blog.title}" has been published!')
            elif decision == 'CHANGES_REQUESTED':
                blog.status = Blog.STATUS_CHANGES
                messages.info(request, f'Changes requested for "{blog.title}".')
            else:
                blog.status = Blog.STATUS_REJECTED
                messages.warning(request, f'"{blog.title}" has been rejected.')

            blog.save()
            return redirect('dashboard:editor')
    else:
        form = ReviewForm()

    return render(request, 'blogs/review_blog.html', {
        'blog': blog,
        'form': form,
        'title': f'Review: {blog.title}',
    })


@login_required
def toggle_feature(request, slug):
    """Superuser/Editor toggles a blog's featured status."""
    if not is_editor(request.user):
        return HttpResponseForbidden()
    blog = get_object_or_404(Blog, slug=slug)
    blog.is_featured = not blog.is_featured
    blog.save()
    status = 'featured' if blog.is_featured else 'unfeatured'
    messages.success(request, f'"{blog.title}" is now {status}.')
    return redirect('blogs:blog_detail', slug=slug)


@login_required
def archive_blog(request, slug):
    """Editor/Superuser archives a published blog."""
    if not is_editor(request.user):
        return HttpResponseForbidden()
    blog = get_object_or_404(Blog, slug=slug)
    blog.status = Blog.STATUS_ARCHIVED
    blog.save()
    messages.success(request, f'"{blog.title}" has been archived.')
    return redirect('dashboard:editor')
