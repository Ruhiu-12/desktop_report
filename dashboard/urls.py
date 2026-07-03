from django.urls import path
from . import views

urlpatterns = [
    # Change 'dashboard_view' to 'dashboard'
    path('', views.dashboard, name='dashboard'),

   
]