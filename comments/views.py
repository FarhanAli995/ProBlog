from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from blogs.models import Blog
from .models import Comment, Report
from .forms import CommentForm, ReplyForm, ReportForm


def is_moderator(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='Moderators').exists()
    )


@login_required
def add_comment(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status=Blog.STATUS_PUBLISHED)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.blog = blog
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment posted!')
    return redirect('blogs:blog_detail', slug=slug)


@login_required
def add_reply(request, slug, comment_id):
    blog = get_object_or_404(Blog, slug=slug, status=Blog.STATUS_PUBLISHED)
    parent = get_object_or_404(Comment, id=comment_id, blog=blog)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            reply = form.save(commit=False)
            reply.blog = blog
            reply.user = request.user
            reply.parent = parent
            reply.save()
            messages.success(request, 'Reply posted!')
    return redirect('blogs:blog_detail', slug=slug)


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    # Allow: own comment, moderator, or superuser
    if comment.user != request.user and not is_moderator(request.user):
        return HttpResponseForbidden()
    slug = comment.blog.slug
    if request.method == 'POST':
        comment.delete()
        messages.success(request, 'Comment deleted.')
    return redirect('blogs:blog_detail', slug=slug)


@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reporter = request.user
            report.comment = comment
            report.save()
            messages.success(request, 'Comment reported. Thank you!')
    return redirect('blogs:blog_detail', slug=comment.blog.slug)


@login_required
def approve_comment(request, comment_id):
    """Moderator approves a hidden comment."""
    if not is_moderator(request.user):
        return HttpResponseForbidden()
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = True
    comment.save()
    messages.success(request, 'Comment approved.')
    return redirect('dashboard:moderator')


@login_required
def hide_comment(request, comment_id):
    """Moderator hides a comment."""
    if not is_moderator(request.user):
        return HttpResponseForbidden()
    comment = get_object_or_404(Comment, id=comment_id)
    comment.is_approved = False
    comment.save()
    messages.success(request, 'Comment hidden.')
    return redirect('dashboard:moderator')


@login_required
def dismiss_report(request, report_id):
    """Moderator dismisses a report."""
    if not is_moderator(request.user):
        return HttpResponseForbidden()
    report = get_object_or_404(Report, id=report_id)
    report.status = Report.STATUS_DISMISSED
    report.reviewed_by = request.user
    report.save()
    messages.success(request, 'Report dismissed.')
    return redirect('dashboard:moderator')
