from django.urls import path
from . import views
from .api import lab_machines_api, issue_templates_api

urlpatterns = [
    path('', views.lab_list, name='lab_list'),
    path('api/machines/', lab_machines_api, name='lab_machines_api'),
    path('api/issues/', issue_templates_api, name='issue_templates_api'),
    path('create/', views.lab_create, name='lab_create'),
    path('<int:lab_id>/delete/', views.lab_delete, name='lab_delete'),
    path('machine/<int:machine_id>/update/', views.machine_update, name='machine_update'),
    path('issue/create/', views.issue_create, name='issue_create'),
    path('issue/<int:issue_id>/delete/', views.issue_delete, name='issue_delete'),
    path('issue/<int:issue_id>/update-priority/', views.issue_update_priority, name='issue_update_priority'),
]
