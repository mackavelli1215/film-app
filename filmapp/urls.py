"""
URL configuration for filmapp project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from core.views import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', DashboardView.as_view(), name='dashboard'),
    
    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', include('accounts.urls')),
    
    # Main app URLs
    path('projects/', include('projects.urls')),
    path('grants/', include('grants.urls')),
    path('agents/', include('agents.urls')),
]