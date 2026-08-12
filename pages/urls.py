from django.urls import path
from . import views
from django.views.generic import TemplateView

app_name = 'pages'

urlpatterns = [
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    path('disclaimer/', TemplateView.as_view(template_name='pages/disclaimer.html'), name='disclaimer'),
]
