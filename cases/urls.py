from django.urls import path
from . import views

urlpatterns = [
    path('', views.case_list, name='case_list'),
    path('create/', views.case_create, name='case_create'),
    path('report/', views.case_create, name='case_create_public'),
    path('<int:case_id>/', views.case_detail, name='case_detail'),
    path('<int:case_id>/assign/', views.case_assign, name='case_assign'),
    path('<int:case_id>/update-status/', views.case_update_status, name='case_update_status'),
    path('<int:case_id>/add-note/', views.case_add_note, name='case_add_note'),
    path('<int:case_id>/review/', views.case_review, name='case_review'),
    path('<int:case_id>/review/add-note/', views.case_review_add_note, name='case_review_add_note'),
    path('<int:case_id>/delete/', views.case_delete, name='case_delete'),
]
