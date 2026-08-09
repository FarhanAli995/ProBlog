import json
from datetime import date, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncMonth, TruncDay
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

def _last_n_months(n, today=None):
    today = today or date.today()
    months = []
    year = today.year
    month = today.month
    for _ in range(n):
        months.append(date(year, month, 1))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))


@login_required
def editor(request):
    if not _is_editor(request.user):
        messages.error(request, 'Editor access required.')
        return redirect('dashboard:home')

    pending = Blog.objects.filter(
        status=Blog.STATUS_PENDING
    ).select_related('author', 'category', 'author__profile').order_by('created_at')

    recent_reviewed = Blog.objects.filter(
        status__in=[Blog.STATUS_PUBLISHED, Blog.STATUS_REJECTED, Blog.STATUS_CHANGES]
    ).select_related('author', 'author__profile').order_by('-updated_at')[:10]

    total_blogs = Blog.objects.count()
    draft_count = Blog.objects.filter(status=Blog.STATUS_DRAFT).count()
    pending_count = pending.count()
    published_count = Blog.objects.filter(status=Blog.STATUS_PUBLISHED).count()
    rejected_count = Blog.objects.filter(status__in=[Blog.STATUS_REJECTED, Blog.STATUS_CHANGES]).count()

    stats = {
        'total_blogs': total_blogs,
        'draft': draft_count,
        'pending': pending_count,
        'published': published_count,
        'rejected': rejected_count,
        'published_today': Blog.objects.filter(
            status=Blog.STATUS_PUBLISHED,
            published_at__date=date.today()
        ).count(),
        'total_published': published_count,
    }

    published = Blog.objects.filter(status=Blog.STATUS_PUBLISHED, published_at__isnull=False)
    month_window = _last_n_months(6)
    monthly_views_qs = published.annotate(month=TruncMonth('published_at')).values('month')
    monthly_views_qs = monthly_views_qs.annotate(total_views=Sum('views')).order_by('month')
    monthly_views = {item['month'].strftime('%Y-%m'): item['total_views'] for item in monthly_views_qs}
    views_over_time = [
        {
            'label': dt.strftime('%b'),
            'value': monthly_views.get(dt.strftime('%Y-%m'), 0)
        }
        for dt in month_window
    ]
    views_max = max([item['value'] for item in views_over_time]) if views_over_time else 1
    if views_max == 0:
        views_max = 1

    top_posts = Blog.objects.filter(status=Blog.STATUS_PUBLISHED).order_by('-views')[:4]

    # Status distribution for donut chart
    status_labels = ['Published', 'Pending', 'Draft']
    status_values = [published_count, pending_count, draft_count]

    # Engagement and other small KPIs
    total_views = published.aggregate(total=Sum('views'))['total'] or 0
    total_likes = Like.objects.filter(blog__status=Blog.STATUS_PUBLISHED).count()
    total_comments = Comment.objects.filter(blog__status=Blog.STATUS_PUBLISHED).count()
    engagement_rate = round(((total_likes + total_comments) / max(total_views, 1)) * 100, 1)

    # Average read time in seconds (estimate from content word count at 200 wpm)
    avg_read_minutes = 0
    pub_count = published.count()
    if pub_count > 0:
        contents = published.values_list('content', flat=True)
        total_words = 0
        for c in contents:
            if not c:
                continue
            total_words += len(c.split())
        words_per_min = 200
        total_read_minutes = (total_words / words_per_min) if words_per_min else 0
        avg_read_minutes = total_read_minutes / pub_count
    avg_read_seconds = int(avg_read_minutes * 60)

    # Review efficiency over last 30 days: ratio of published posts to (published + pending)
    last_30 = date.today() - timedelta(days=30)
    resolved_30 = Blog.objects.filter(status=Blog.STATUS_PUBLISHED, published_at__date__gte=last_30).count()
    pending_30 = Blog.objects.filter(status=Blog.STATUS_PENDING, created_at__date__gte=last_30).count()
    review_efficiency = int((resolved_30 / max((resolved_30 + pending_30), 1)) * 100)

    return render(request, 'dashboard/editor.html', {
        'pending': pending,
        'recent_reviewed': recent_reviewed,
        'stats': stats,
        'views_over_time_json': json.dumps(views_over_time),
        'views_max': views_max,
        'top_posts': top_posts,
        'status_labels_json': json.dumps(status_labels),
        'status_values_json': json.dumps(status_values),
        'total_views': total_views,
        'engagement_rate': engagement_rate,
        'avg_read_seconds': avg_read_seconds,
        'review_efficiency': review_efficiency,
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
    pending_count = Blog.objects.filter(status=Blog.STATUS_PENDING).count()

    # Recent users
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:10]

    published = Blog.objects.filter(status=Blog.STATUS_PUBLISHED, published_at__isnull=False)
    month_window = _last_n_months(6)
    monthly_views_qs = published.annotate(month=TruncMonth('published_at')).values('month')
    monthly_views_qs = monthly_views_qs.annotate(total_views=Sum('views')).order_by('month')
    monthly_views = {item['month'].strftime('%Y-%m'): item['total_views'] for item in monthly_views_qs}
    views_over_time = [
        {
            'label': dt.strftime('%b'),
            'value': monthly_views.get(dt.strftime('%Y-%m'), 0)
        }
        for dt in month_window
    ]
    views_max = max([item['value'] for item in views_over_time]) if views_over_time else 1
    if views_max == 0:
        views_max = 1

    total_views = published.aggregate(total=Sum('views'))['total'] or 0
    seven_days_ago = date.today() - timedelta(days=6)
    pending_daily_qs = Blog.objects.filter(
        status=Blog.STATUS_PENDING,
        created_at__date__gte=seven_days_ago
    ).annotate(day=TruncDay('created_at')).values('day').annotate(total=Count('id')).order_by('day')
    pending_daily = {item['day'].strftime('%Y-%m-%d'): item['total'] for item in pending_daily_qs}
    risk_trend = [
        {
            'label': (seven_days_ago + timedelta(days=i)).strftime('%b %d'),
            'value': pending_daily.get((seven_days_ago + timedelta(days=i)).strftime('%Y-%m-%d'), 0)
        }
        for i in range(7)
    ]
    risk_level = 'High' if pending_count > max(total_blogs // 5, 1) else 'Moderate' if pending_count > 0 else 'Low'

    # Blog distribution by status
    blog_stats = {
        'draft': Blog.objects.filter(status=Blog.STATUS_DRAFT).count(),
        'pending': Blog.objects.filter(status=Blog.STATUS_PENDING).count(),
        'published': Blog.objects.filter(status=Blog.STATUS_PUBLISHED).count(),
        'rejected': Blog.objects.filter(status=Blog.STATUS_REJECTED).count(),
        'archived': Blog.objects.filter(status=Blog.STATUS_ARCHIVED).count(),
    }

    status_labels = ['Draft', 'Pending', 'Published', 'Rejected', 'Archived']
    status_values = [
        blog_stats['draft'],
        blog_stats['pending'],
        blog_stats['published'],
        blog_stats['rejected'],
        blog_stats['archived'],
    ]

    # Group counts
    groups = {
        'editors': User.objects.filter(groups__name='Editors').count(),
        'moderators': User.objects.filter(groups__name='Moderators').count(),
        'authors': User.objects.filter(groups__name='Authors').count(),
    }

    # Top authors by views
    top_authors = User.objects.annotate(
        total_views=Sum('blogs__views'),
        post_count=Count('blogs')
    ).filter(post_count__gt=0).order_by('-total_views')[:5]

    group_labels = json.dumps(['Editors', 'Moderators', 'Authors'])
    group_values = json.dumps([
        groups['editors'],
        groups['moderators'],
        groups['authors'],
    ])

    top_posts = Blog.objects.filter(status=Blog.STATUS_PUBLISHED).order_by('-views')[:4]

    top_categories = Category.objects.annotate(post_count=Count('blogs')).order_by('-post_count')[:5]
    asset_labels = json.dumps([cat.name for cat in top_categories])
    asset_values = json.dumps([cat.post_count for cat in top_categories])

    return render(request, 'dashboard/superuser.html', {
        'total_users': total_users,
        'total_blogs': total_blogs,
        'total_comments': total_comments,
        'total_reports': total_reports,
        'recent_users': recent_users,
        'blog_stats': blog_stats,
        'status_labels': json.dumps(['Draft', 'Pending', 'Published', 'Rejected', 'Archived']),
        'status_values': json.dumps([
            blog_stats['draft'],
            blog_stats['pending'],
            blog_stats['published'],
            blog_stats['rejected'],
            blog_stats['archived'],
        ]),
        'group_labels': group_labels,
        'group_values': group_values,
        'top_authors': top_authors,
        'top_posts': top_posts,
        'views_over_time_json': json.dumps(views_over_time),
        'risk_trend_json': json.dumps(risk_trend),
        'asset_labels': asset_labels,
        'asset_values': asset_values,
        'total_exposure': total_views,
        'open_positions': pending_count,
        'risk_level': risk_level,
        'active_alerts': total_reports,
        'views_max': max([item['value'] for item in views_over_time]) if views_over_time else 1,
        'groups': groups,
        'categories': top_categories,
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
