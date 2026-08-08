from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Profile (edit must come before the dynamic username route)
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.ProfileDetailView.as_view(), name='profile'),

    # Password change
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='password_change'),

    # Password reset
    path('password/reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password/reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password/reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # Account deletion
    path('delete/', views.delete_account, name='delete_account'),
]
