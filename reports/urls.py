from django.urls import path
from . import views

urlpatterns = [
    path('', views.report_list, name='report_list'),
    path('<int:report_id>/', views.report_detail, name='report_detail'),
    path('create/<int:case_id>/', views.report_create, name='report_create'),
    path('<int:report_id>/review/', views.report_review, name='report_review'),
]
