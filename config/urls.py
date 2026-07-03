from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

from cases import views

urlpatterns = [
    path('', lambda request: redirect('login')),
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    # Optional: redirect root to login
    path('', include('accounts.urls')), 
   
]