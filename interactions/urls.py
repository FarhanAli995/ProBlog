from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    path('like/<slug:slug>/', views.toggle_like, name='toggle_like'),
    path('bookmark/<slug:slug>/', views.toggle_bookmark, name='toggle_bookmark'),
    path('follow/<str:username>/', views.toggle_follow, name='toggle_follow'),
]
