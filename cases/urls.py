from django.urls import path
from . import views

urlpatterns = [
    path('', views.case_list, name='case_list'),
    path('create/', views.case_create, name='case_create'),
    path('<int:case_id>/', views.case_detail, name='case_detail'),
    path('<int:case_id>/assign/', views.case_assign, name='case_assign'),
    path('<int:case_id>/update-status/', views.case_update_status, name='case_update_status'),
    path('<int:case_id>/add-note/', views.case_add_note, name='case_add_note'),
]
