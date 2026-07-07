from django.urls import path
from . import views

urlpatterns = [
    path('', views.log_list, name='log_list'),
    path('download/', views.log_download, name='log_download'),
    path('feedback/', views.feedback_list, name='feedback_list'),
    path('feedback/submit/', views.feedback_submit, name='feedback_submit'),
    path('feedback/<int:feedback_id>/', views.feedback_detail, name='feedback_detail'),
]
