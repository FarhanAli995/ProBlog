from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('dashboard/', views.home, name='home'),
    path('dashboard/author/', views.author, name='author'),
    path('dashboard/editor/', views.editor, name='editor'),
    path('dashboard/moderator/', views.moderator, name='moderator'),
    path('dashboard/superuser/', views.superuser, name='superuser'),
    path('dashboard/users/', views.manage_users, name='manage_users'),
    path('dashboard/users/<int:user_id>/role/', views.assign_role, name='assign_role'),
    path('dashboard/users/<int:user_id>/toggle-active/', views.toggle_user_active, name='toggle_user_active'),
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
]
