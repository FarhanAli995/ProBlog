from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from pages.views import health_check

urlpatterns = [
    path('admin/', include('customadmin.urls')),
    path('accounts/', include('accounts.urls')),
    path('health/', health_check, name='health_check'),
    path('', include('pages.urls')),
    path('', include('blogs.urls')),
    path('', include('comments.urls')),
    path('', include('interactions.urls')),
    path('', include('dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
