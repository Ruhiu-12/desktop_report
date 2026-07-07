from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_list, name='user_list'),
    path('<int:user_id>/', views.user_detail, name='user_detail'),
    path('<int:user_id>/update-role/', views.user_update_role, name='user_update_role'),
    path('<int:user_id>/delete/', views.user_delete, name='user_delete'),
]
