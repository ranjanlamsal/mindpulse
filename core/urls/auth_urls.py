"""
Authentication URL patterns.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from core.views.auth_views import (
    CustomTokenObtainPairView,
    UserRegistrationView, 
    UserProfileView,
    ChangePasswordView,
    LogoutView,
    employee_dashboard,
    manager_dashboard,
    admin_dashboard
)

urlpatterns = [
    # Authentication endpoints
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    
    # User management endpoints
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    
    # Role-based dashboards
    path('dashboard/employee/', employee_dashboard, name='employee_dashboard'),
    path('dashboard/manager/', manager_dashboard, name='manager_dashboard'),
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
]