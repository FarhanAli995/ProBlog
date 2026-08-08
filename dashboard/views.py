from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Count, Sum, Q
from django.core.paginator import Paginator

from blogs.models import Blog, Category, Tag
from comments.models import Comment, Report
from interactions.models import Like, Bookmark, Follow


# ─── Role Helpers ──────────────────────────────────────────────────────────────

def _is_editor(user):
    return user.is_superuser or user.groups.filter(name='Editors').exists()

def _is_moderator(user):
    return user.is_superuser or user.groups.filter(name='Moderators').exists()

def _is_author(user):
    return user.is_superuser or user.groups.filter(name__in=['Authors', 'Editors']).exists()


# ─── Reader / Default Dashboard ───────────────────────────────────────────────

@login_required
def home(request):
    """Redirect to the most-privileged dashboard the user can access."""
    if request.user.is_superuser:
        return redirect('dashboard:superuser')
    if _is_editor(request.user):
        return redirect('dashboard:editor')
    if _is_moderator(request.user):
        return redirect('dashboard:moderator')
    if _is_author(request.user):
        return redirect('dashboard:author')

    # Regular reader dashboard
    bookmarks = Bookmark.objects.filter(user=request.user).select_related(
        'blog', 'blog__author', 'blog__author__profile'
    )[:6]
    following = Follow.objects.filter(follower=request.user).select_related(
        'following', 'following__profile'
    )[:8]
    return render(request, 'dashboard/home.html', {
        'bookmarks': bookmarks,
        'following': following,
        'title': 'My Dashboard',
    })


# ─── Author Dashboard ─────────────────────────────────────────────────────────

@login_required
def author(request):
    if not _is_author(request.user):
        messages.error(request, 'Author access required.')
        return redirect('dashboard:home')

    target_user = request.user
    # Superuser can view any author's posts
    if request.user.is_superuser and request.GET.get('author_id'):
        target_user = get_object_or_404(User, id=request.GET.get('author_id'))

    all_posts = Blog.objects.filter(author=target_user).order_by('-created_at')

    # Stats
    stats = {
        'total': all_posts.count(),
        'draft': all_posts.filter(status=Blog.STATUS_DRAFT).count(),
        'pending': all_posts.filter(status=Blog.STATUS_PENDING).count(),
        'published': all_posts.filter(status=Blog.STATUS_PUBLISHED).count(),
        'rejected': all_posts.filter(status__in=[Blog.STATUS_REJECTED, Blog.STATUS_CHANGES]).count(),
        'total_views': all_posts.aggregate(total=Sum('views'))['total'] or 0,
        'total_likes': Like.objects.filter(blog__author=target_user).count(),
    }

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        all_posts = all_posts.filter(status=status_filter)

    paginator = Paginator(all_posts, 10)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/author.html', {
        'page_obj': page_obj,
        'stats': stats,
        'target_user': target_user,
        'status_filter': status_filter,
        'status_choices': Blog.STATUS_CHOICES,
        'title': 'Author Dashboard',
    })


# ─── Editor Dashboard ─────────────────────────────────────────────────────────

@login_required
def editor(request):
    if not _is_editor(request.user):
        messages.error(request, 'Editor access required.')
        return redirect('dashboard:home')

    pending = Blog.objects.filter(
        status=Blog.STATUS_PENDING
    ).select_related('author', 'category', 'author__profile').order_by('created_at')

    # Recently reviewed
    recent_reviewed = Blog.objects.filter(
        status__in=[Blog.STATUS_PUBLISHED, Blog.STATUS_REJECTED, Blog.STATUS_CHANGES]
    ).select_related('author', 'author__profile').order_by('-updated_at')[:10]

    stats = {
        'pending': pending.count(),
        'published_today': Blog.objects.filter(
            status=Blog.STATUS_PUBLISHED,
            published_at__date=__import__('datetime').date.today()
        ).count(),
        'total_published': Blog.objects.filter(status=Blog.STATUS_PUBLISHED).count(),
    }

    return render(request, 'dashboard/editor.html', {
        'pending': pending,
        'recent_reviewed': recent_reviewed,
        'stats': stats,
        'title': 'Editor Dashboard',
    })


# ─── Moderator Dashboard ──────────────────────────────────────────────────────

@login_required
def moderator(request):
    if not _is_moderator(request.user):
        messages.error(request, 'Moderator access required.')
        return redirect('dashboard:home')

    pending_reports = Report.objects.filter(
        status=Report.STATUS_PENDING
    ).select_related('reporter', 'comment', 'comment__user', 'blog').order_by('-created_at')

    hidden_comments = Comment.objects.filter(
        is_approved=False
    ).select_related('user', 'blog').order_by('-created_at')[:20]

    recent_comments = Comment.objects.filter(
        is_approved=True
    ).select_related('user', 'blog').order_by('-created_at')[:20]

    stats = {
        'pending_reports': pending_reports.count(),
        'hidden_comments': Comment.objects.filter(is_approved=False).count(),
        'total_comments': Comment.objects.count(),
    }

    paginator = Paginator(pending_reports, 15)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/moderator.html', {
        'page_obj': page_obj,
        'hidden_comments': hidden_comments,
        'recent_comments': recent_comments,
        'stats': stats,
        'title': 'Moderator Dashboard',
    })


# ─── Superuser Dashboard ──────────────────────────────────────────────────────

@login_required
def superuser(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    # Site-wide stats
    total_users = User.objects.count()
    total_blogs = Blog.objects.count()
    total_comments = Comment.objects.count()
    total_reports = Report.objects.filter(status=Report.STATUS_PENDING).count()

    # Recent users
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:10]

    # Blog distribution by status
    blog_stats = {
        'draft': Blog.objects.filter(status=Blog.STATUS_DRAFT).count(),
        'pending': Blog.objects.filter(status=Blog.STATUS_PENDING).count(),
        'published': Blog.objects.filter(status=Blog.STATUS_PUBLISHED).count(),
        'rejected': Blog.objects.filter(status=Blog.STATUS_REJECTED).count(),
        'archived': Blog.objects.filter(status=Blog.STATUS_ARCHIVED).count(),
    }

    # Top authors by views
    from django.db.models import Sum
    top_authors = User.objects.annotate(
        total_views=Sum('blogs__views'),
        post_count=Count('blogs')
    ).filter(post_count__gt=0).order_by('-total_views')[:5]

    # Group counts
    groups = {
        'editors': User.objects.filter(groups__name='Editors').count(),
        'moderators': User.objects.filter(groups__name='Moderators').count(),
        'authors': User.objects.filter(groups__name='Authors').count(),
    }

    return render(request, 'dashboard/superuser.html', {
        'total_users': total_users,
        'total_blogs': total_blogs,
        'total_comments': total_comments,
        'total_reports': total_reports,
        'recent_users': recent_users,
        'blog_stats': blog_stats,
        'top_authors': top_authors,
        'groups': groups,
        'categories': Category.objects.annotate(post_count=Count('blogs')).order_by('-post_count')[:5],
        'title': 'Superuser Dashboard',
    })


# ─── Superuser: Manage Users ──────────────────────────────────────────────────

@login_required
def manage_users(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    q = request.GET.get('q', '').strip()
    users_qs = User.objects.select_related('profile').prefetch_related('groups').order_by('-date_joined')
    if q:
        users_qs = users_qs.filter(
            Q(username__icontains=q) | Q(email__icontains=q) |
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )

    paginator = Paginator(users_qs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'dashboard/manage_users.html', {
        'page_obj': page_obj,
        'q': q,
        'title': 'Manage Users',
    })


@login_required
def assign_role(request, user_id):
    """Superuser assigns/removes a user's group role."""
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    target = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        role = request.POST.get('role', '')
        action = request.POST.get('action', 'add')

        valid_roles = ['Authors', 'Editors', 'Moderators']
        if role not in valid_roles:
            messages.error(request, 'Invalid role.')
            return redirect('dashboard:manage_users')

        group, _ = Group.objects.get_or_create(name=role)
        if action == 'add':
            target.groups.add(group)
            messages.success(request, f'{target.username} added to {role}.')
        else:
            target.groups.remove(group)
            messages.success(request, f'{target.username} removed from {role}.')

        # Toggle staff status for Editors/Moderators
        if role in ('Editors', 'Moderators'):
            target.is_staff = target.groups.filter(name__in=['Editors', 'Moderators']).exists()
            target.save()

    return redirect('dashboard:manage_users')


@login_required
def toggle_user_active(request, user_id):
    """Superuser activate/deactivate a user account."""
    if not request.user.is_superuser:
        return HttpResponseForbidden()
    target = get_object_or_404(User, id=user_id)
    if target == request.user:
        messages.error(request, 'You cannot deactivate yourself.')
        return redirect('dashboard:manage_users')
    if request.method == 'POST':
        target.is_active = not target.is_active
        target.save()
        status = 'activated' if target.is_active else 'deactivated'
        messages.success(request, f'User {target.username} has been {status}.')
    return redirect('dashboard:manage_users')


@login_required
def bookmarks_view(request):
    """User's bookmarked articles."""
    bookmarks = Bookmark.objects.filter(user=request.user).select_related(
        'blog', 'blog__author', 'blog__author__profile', 'blog__category'
    ).order_by('-created_at')
    paginator = Paginator(bookmarks, 9)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'dashboard/bookmarks.html', {
        'page_obj': page_obj,
        'title': 'My Bookmarks',
    })
