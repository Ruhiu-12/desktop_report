from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect, render
from django.conf import settings
from django.conf.urls.static import static

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, 'home.html')

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('dashboard/', include('dashboard.urls')),
    path('accounts/', include('accounts.urls')),
    path('cases/', include('cases.urls')),
    path('reports/', include('reports.urls')),
    path('users/', include('users.urls')),
    path('logs/', include('logs.urls')),
    path('labs/', include('labs.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)