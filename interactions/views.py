from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from blogs.models import Blog
from .models import Like, Bookmark, Follow
from django.contrib.auth.models import User


@login_required
def toggle_like(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status=Blog.STATUS_PUBLISHED)
    like, created = Like.objects.get_or_create(user=request.user, blog=blog)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    count = blog.likes.count()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'count': count})
    return redirect('blogs:blog_detail', slug=slug)


@login_required
def toggle_bookmark(request, slug):
    blog = get_object_or_404(Blog, slug=slug, status=Blog.STATUS_PUBLISHED)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, blog=blog)
    if not created:
        bookmark.delete()
        bookmarked = False
        messages.info(request, f'Removed "{blog.title}" from bookmarks.')
    else:
        bookmarked = True
        messages.success(request, f'"{blog.title}" bookmarked!')
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'bookmarked': bookmarked})
    return redirect('blogs:blog_detail', slug=slug)


@login_required
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.warning(request, 'You cannot follow yourself.')
        return redirect('accounts:profile', username=username)
    follow, created = Follow.objects.get_or_create(
        follower=request.user, following=target
    )
    if not created:
        follow.delete()
        messages.info(request, f'Unfollowed {target.username}.')
    else:
        messages.success(request, f'Now following {target.username}!')
    return redirect('accounts:profile', username=username)
