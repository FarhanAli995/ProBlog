from django.urls import path
from . import views

app_name = 'customadmin'

urlpatterns = [
    path('', views.admin_home, name='home'),
    path('<slug:slug>/', views.section_list, name='section_list'),
    path('<slug:slug>/add/', views.section_add, name='section_add'),
    path('<slug:slug>/<int:pk>/edit/', views.section_edit, name='section_edit'),
    path('<slug:slug>/<int:pk>/delete/', views.section_delete, name='section_delete'),
    path('reports/<int:pk>/resolve/<str:new_status>/', views.report_resolve, name='report_resolve'),
]
