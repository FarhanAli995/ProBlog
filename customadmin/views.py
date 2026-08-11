import json
from datetime import date

from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.db.models.functions import TruncMonth
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import Http404

from blogs.models import Blog, Category
from comments.models import Comment, Report
from interactions.models import Like, Bookmark, Follow

from .registry import REGISTRY_BY_SLUG, grouped_sections


def _last_n_months(n, today=None):
    today = today or date.today()
    months = []
    year, month = today.year, today.month
    for _ in range(n):
        months.append(date(year, month, 1))
        month -= 1
        if month == 0:
            month, year = 12, year - 1
    return list(reversed(months))


def _is_staff(user):
    return user.is_active and user.is_staff


staff_required = user_passes_test(_is_staff, login_url='accounts:login')


def _get_section(slug):
    section = REGISTRY_BY_SLUG.get(slug)
    if section is None:
        raise Http404('Unknown admin section')
    return section


def _common_context(request, active_slug=None):
    return {
        'nav_groups': grouped_sections(),
        'active_slug': active_slug,
    }


# ─── Overview ──────────────────────────────────────────────────────────────

@login_required
@staff_required
def admin_home(request):
    context = _common_context(request, active_slug=None)

    total_blogs = Blog.objects.count()

    blog_stats = {
        'draft': Blog.objects.filter(status=Blog.STATUS_DRAFT).count(),
        'pending': Blog.objects.filter(status=Blog.STATUS_PENDING).count(),
        'published': Blog.objects.filter(status=Blog.STATUS_PUBLISHED).count(),
        'rejected': Blog.objects.filter(status=Blog.STATUS_REJECTED).count(),
        'archived': Blog.objects.filter(status=Blog.STATUS_ARCHIVED).count(),
    }
    status_labels = ['Draft', 'Pending', 'Published', 'Rejected', 'Archived']
    status_values = [blog_stats['draft'], blog_stats['pending'], blog_stats['published'],
                      blog_stats['rejected'], blog_stats['archived']]

    # Views trend — last 6 months of published views
    published = Blog.objects.filter(status=Blog.STATUS_PUBLISHED, published_at__isnull=False)
    month_window = _last_n_months(6)
    monthly_views_qs = published.annotate(month=TruncMonth('published_at')).values('month')
    monthly_views_qs = monthly_views_qs.annotate(total_views=Sum('views')).order_by('month')
    monthly_views = {item['month'].strftime('%Y-%m'): item['total_views'] for item in monthly_views_qs}
    views_over_time = [
        {'label': dt.strftime('%b'), 'value': monthly_views.get(dt.strftime('%Y-%m'), 0)}
        for dt in month_window
    ]

    # Signups trend — last 6 months of new users
    monthly_signups_qs = User.objects.annotate(month=TruncMonth('date_joined')).values('month')
    monthly_signups_qs = monthly_signups_qs.annotate(total=Count('id')).order_by('month')
    monthly_signups = {item['month'].strftime('%Y-%m'): item['total'] for item in monthly_signups_qs}
    signups_over_time = [
        {'label': dt.strftime('%b'), 'value': monthly_signups.get(dt.strftime('%Y-%m'), 0)}
        for dt in month_window
    ]

    # Engagement split — likes / bookmarks / follows / comments
    total_likes = Like.objects.count()
    total_bookmarks = Bookmark.objects.count()
    total_follows = Follow.objects.count()
    total_comments = Comment.objects.count()

    context.update({
        'total_users': User.objects.count(),
        'total_blogs': total_blogs,
        'total_comments': total_comments,
        'pending_reports': Report.objects.filter(status=Report.STATUS_PENDING).count(),
        'total_categories': Category.objects.count(),
        'total_likes': total_likes,
        'total_bookmarks': total_bookmarks,
        'total_follows': total_follows,
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_blogs': Blog.objects.select_related('author').order_by('-created_at')[:5],
        'blog_stats': blog_stats,
        'status_labels_json': json.dumps(status_labels),
        'status_values_json': json.dumps(status_values),
        'views_over_time_json': json.dumps(views_over_time),
        'signups_over_time_json': json.dumps(signups_over_time),
        'engagement_labels_json': json.dumps(['Likes', 'Bookmarks', 'Follows', 'Comments']),
        'engagement_values_json': json.dumps([total_likes, total_bookmarks, total_follows, total_comments]),
        'title': 'ProBlog Admin',
    })
    return render(request, 'customadmin/home.html', context)


# ─── Generic list ──────────────────────────────────────────────────────────

@login_required
@staff_required
def section_list(request, slug):
    section = _get_section(slug)
    qs = section.model.objects.all()

    if section.ordering:
        qs = qs.order_by(section.ordering)

    q = request.GET.get('q', '').strip()
    if q and section.search_fields:
        filter_q = Q()
        for field in section.search_fields:
            filter_q |= Q(**{f'{field}__icontains': q})
        qs = qs.filter(filter_q)

    active_filters = {}
    for field_name, _label in section.list_filter:
        value = request.GET.get(field_name, '')
        if value != '':
            qs = qs.filter(**{field_name: value})
            active_filters[field_name] = value

    paginator = Paginator(qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = _common_context(request, active_slug=slug)
    context.update({
        'section': section,
        'page_obj': page_obj,
        'q': q,
        'active_filters': active_filters,
        'title': section.verbose_name_plural,
    })
    return render(request, 'customadmin/list.html', context)


# ─── Generic add / edit ────────────────────────────────────────────────────

@login_required
@staff_required
def section_add(request, slug):
    section = _get_section(slug)
    if not section.can_add:
        messages.error(request, f'Adding {section.verbose_name_plural} is not allowed here.')
        return redirect('customadmin:section_list', slug=slug)

    form_class = section.form_class
    if section.model is User:
        from .forms import UserCreateForm
        form_class = UserCreateForm

    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, f'{section.verbose_name} created successfully.')
            return redirect('customadmin:section_list', slug=slug)
    else:
        form = form_class()

    context = _common_context(request, active_slug=slug)
    context.update({
        'section': section,
        'form': form,
        'is_add': True,
        'title': f'Add {section.verbose_name}',
    })
    return render(request, 'customadmin/form.html', context)


@login_required
@staff_required
def section_edit(request, slug, pk):
    section = _get_section(slug)
    if not section.can_edit:
        messages.error(request, f'Editing {section.verbose_name_plural} is not allowed here.')
        return redirect('customadmin:section_list', slug=slug)

    obj = get_object_or_404(section.model, pk=pk)

    if request.method == 'POST':
        form = section.form_class(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, f'{section.verbose_name} updated successfully.')
            return redirect('customadmin:section_list', slug=slug)
    else:
        form = section.form_class(instance=obj)

    context = _common_context(request, active_slug=slug)
    context.update({
        'section': section,
        'form': form,
        'obj': obj,
        'is_add': False,
        'title': f'Edit {section.verbose_name}',
    })
    return render(request, 'customadmin/form.html', context)


# ─── Generic delete ─────────────────────────────────────────────────────────

@login_required
@staff_required
def section_delete(request, slug, pk):
    section = _get_section(slug)
    if not section.can_delete:
        messages.error(request, f'Deleting {section.verbose_name_plural} is not allowed here.')
        return redirect('customadmin:section_list', slug=slug)

    obj = get_object_or_404(section.model, pk=pk)

    if section.model is User and obj == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('customadmin:section_list', slug=slug)

    if request.method == 'POST':
        obj.delete()
        messages.success(request, f'{section.verbose_name} deleted successfully.')
        return redirect('customadmin:section_list', slug=slug)

    context = _common_context(request, active_slug=slug)
    context.update({
        'section': section,
        'obj': obj,
        'title': f'Delete {section.verbose_name}',
    })
    return render(request, 'customadmin/confirm_delete.html', context)


# ─── Moderation quick actions ───────────────────────────────────────────────

@login_required
@staff_required
def report_resolve(request, pk, new_status):
    if new_status not in (Report.STATUS_REVIEWED, Report.STATUS_DISMISSED):
        raise Http404()
    report = get_object_or_404(Report, pk=pk)
    if request.method == 'POST':
        report.status = new_status
        report.reviewed_by = request.user
        report.save(update_fields=['status', 'reviewed_by'])
        messages.success(request, f'Report #{report.pk} marked as {report.get_status_display()}.')
    return redirect('customadmin:section_list', slug='reports')
