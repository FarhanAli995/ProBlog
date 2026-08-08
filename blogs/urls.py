from django.urls import path
from . import views

app_name = 'blogs'

urlpatterns = [
    # Public
    path('', views.home, name='home'),
    path('blogs/', views.home, name='blog_list'),
    path('blogs/create/', views.blog_create, name='blog_create'),
    path('blogs/<slug:slug>/edit/', views.blog_edit, name='blog_edit'),
    path('blogs/<slug:slug>/delete/', views.blog_delete, name='blog_delete'),
    path('blogs/<slug:slug>/submit/', views.blog_submit, name='blog_submit'),
    path('blogs/<slug:slug>/review/', views.review_blog, name='review_blog'),
    path('blogs/<slug:slug>/feature/', views.toggle_feature, name='toggle_feature'),
    path('blogs/<slug:slug>/archive/', views.archive_blog, name='archive_blog'),
    path('blogs/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/<slug:slug>/', views.category_detail, name='category_detail'),
    path('authors/', views.author_list, name='author_list'),

]
