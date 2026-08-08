from django.urls import path
from . import views

app_name = 'comments'

urlpatterns = [
    path('blogs/<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('blogs/<slug:slug>/reply/<int:comment_id>/', views.add_reply, name='add_reply'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path('comment/<int:comment_id>/report/', views.report_comment, name='report_comment'),
    path('comment/<int:comment_id>/approve/', views.approve_comment, name='approve_comment'),
    path('comment/<int:comment_id>/hide/', views.hide_comment, name='hide_comment'),
    path('report/<int:report_id>/dismiss/', views.dismiss_report, name='dismiss_report'),
]
