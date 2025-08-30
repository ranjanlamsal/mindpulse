"""
Authentication views for JWT token-based authentication.
"""
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import update_session_auth_hash
from django.utils import timezone

from core.serializers import (
    UserRegistrationSerializer, LoginSerializer, UserProfileSerializer,
    UserUpdateSerializer, PasswordChangeSerializer
)
from core.utils.response_builder import APIResponseBuilder
from core.permissions import IsEmployee, IsManager, IsAdmin
from core.models.user_model import User
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with additional user data.
    """
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Update last login
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            # Prepare response data
            user_data = UserProfileSerializer(user).data
            
            response_data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data
            }
            
            logger.info(f"User {user.username} logged in successfully")
            return APIResponseBuilder.success(
                data=response_data,
                message="Login successful",
                status_code=status.HTTP_200_OK
            )
        else:
            logger.warning(f"Failed login attempt: {serializer.errors}")
            return APIResponseBuilder.error(
                message="Invalid credentials",
                errors=serializer.errors,
                status_code=status.HTTP_401_UNAUTHORIZED
            )


class UserRegistrationView(APIView):
    """
    User registration view (employees only).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens for immediate login
            refresh = RefreshToken.for_user(user)
            user_data = UserProfileSerializer(user).data
            
            response_data = {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': user_data
            }
            
            logger.info(f"New user registered: {user.username}")
            return APIResponseBuilder.success(
                data=response_data,
                message="Registration successful",
                status_code=status.HTTP_201_CREATED
            )
        else:
            return APIResponseBuilder.error(
                message="Registration failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class UserProfileView(APIView):
    """
    View for getting and updating user profile.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """Get user profile."""
        serializer = UserProfileSerializer(request.user)
        return APIResponseBuilder.success(
            data=serializer.data,
            message="Profile retrieved successfully"
        )

    def patch(self, request):
        """Update user profile."""
        serializer = UserUpdateSerializer(
            request.user, 
            data=request.data, 
            partial=True,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {request.user.username} updated profile")
            return APIResponseBuilder.success(
                data=serializer.data,
                message="Profile updated successfully"
            )
        else:
            return APIResponseBuilder.error(
                message="Profile update failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class ChangePasswordView(APIView):
    """
    View for changing user password.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            
            # Update session auth hash to prevent logout
            update_session_auth_hash(request, request.user)
            
            logger.info(f"User {request.user.username} changed password")
            return APIResponseBuilder.success(
                message="Password changed successfully"
            )
        else:
            return APIResponseBuilder.error(
                message="Password change failed",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    """
    Logout view that blacklists the refresh token.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"User {request.user.username} logged out")
            return APIResponseBuilder.success(
                message="Logout successful"
            )
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return APIResponseBuilder.error(
                message="Logout failed",
                status_code=status.HTTP_400_BAD_REQUEST
            )


@api_view(['GET'])
@permission_classes([IsEmployee])
def employee_dashboard(request):
    """
    Dashboard endpoint for employees - access to chatbot and basic features.
    """
    user = request.user
    dashboard_data = {
        'user': UserProfileSerializer(user).data,
        'available_features': [
            'chatbot',
            'profile_management'
        ],
        'message': f'Welcome to your dashboard, {user.username}!'
    }
    
    return APIResponseBuilder.success(
        data=dashboard_data,
        message="Employee dashboard loaded"
    )


@api_view(['GET'])
@permission_classes([IsManager])
def manager_dashboard(request):
    """
    Dashboard endpoint for managers - access to analytics and team data.
    """
    user = request.user
    
    # Get team statistics (simplified)
    total_employees = User.objects.filter(role='employee').count()
    active_employees = User.objects.filter(role='employee', is_active=True).count()
    
    dashboard_data = {
        'user': UserProfileSerializer(user).data,
        'team_stats': {
            'total_employees': total_employees,
            'active_employees': active_employees,
        },
        'available_features': [
            'analytics_dashboard',
            'team_wellbeing_reports',
            'message_analytics',
            'profile_management'
        ],
        'message': f'Welcome to the management dashboard, {user.username}!'
    }
    
    return APIResponseBuilder.success(
        data=dashboard_data,
        message="Manager dashboard loaded"
    )


@api_view(['GET'])
@permission_classes([IsAdmin])
def admin_dashboard(request):
    """
    Dashboard endpoint for admins - full system access.
    """
    user = request.user
    
    # Get system statistics
    total_users = User.objects.count()
    total_employees = User.objects.filter(role='employee').count()
    total_managers = User.objects.filter(role='manager').count()
    total_admins = User.objects.filter(role='admin').count()
    
    dashboard_data = {
        'user': UserProfileSerializer(user).data,
        'system_stats': {
            'total_users': total_users,
            'total_employees': total_employees,
            'total_managers': total_managers,
            'total_admins': total_admins,
        },
        'available_features': [
            'admin_panel',
            'user_management', 
            'system_analytics',
            'full_message_access',
            'analytics_dashboard',
            'team_wellbeing_reports',
            'profile_management'
        ],
        'message': f'Welcome to the admin dashboard, {user.username}!'
    }
    
    return APIResponseBuilder.success(
        data=dashboard_data,
        message="Admin dashboard loaded"
    )