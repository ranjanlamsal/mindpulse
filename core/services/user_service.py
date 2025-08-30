"""
Business logic for user operations.
Separated from views for better maintainability and testability.
"""
from django.contrib.auth import authenticate
from django.db import transaction
from core.models.user_model import User
from core.exceptions import AuthenticationError, ValidationError, InvalidUserError
from core.utils.validators import UUIDValidator
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service class handling user business logic."""
    
    @staticmethod
    @transaction.atomic
    def create_user(user_data: Dict[str, Any]) -> User:
        """
        Create a new user with validation.
        
        Args:
            user_data: Dictionary containing user information
            
        Returns:
            Created User instance
            
        Raises:
            ValidationError: If user data is invalid
        """
        try:
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                role=user_data.get('role', 'employee')
            )
            logger.info(f"User created successfully: {user.username}")
            return user
            
        except Exception as e:
            logger.error(f"Failed to create user {user_data.get('username')}: {str(e)}")
            raise ValidationError(f"Failed to create user: {str(e)}")
    
    @staticmethod
    def authenticate_user(username: str, password: str) -> Optional[User]:
        """
        Authenticate user credentials.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            User instance if authentication successful, None otherwise
            
        Raises:
            AuthenticationError: If authentication fails
        """
        try:
            user = authenticate(username=username, password=password)
            if user and user.is_active:
                logger.info(f"User authenticated successfully: {username}")
                return user
            else:
                logger.warning(f"Authentication failed for user: {username}")
                raise AuthenticationError("Invalid credentials", username=username)
                
        except Exception as e:
            logger.error(f"Authentication error for {username}: {str(e)}")
            raise AuthenticationError("Authentication failed", username=username)
    
    @staticmethod
    def get_user_by_hash(user_hash: str) -> User:
        """
        Get user by their hashed ID.
        
        Args:
            user_hash: User's UUID hash
            
        Returns:
            User instance
            
        Raises:
            InvalidUserError: If user not found
        """
        try:
            validated_uuid = UUIDValidator.validate_uuid(user_hash, "user_hash")
            user = User.objects.get(hashed_id=validated_uuid, is_active=True)
            return user
            
        except User.DoesNotExist:
            logger.warning(f"User not found with hash: {user_hash}")
            raise InvalidUserError("User not found", user_id=user_hash)
        except Exception as e:
            logger.error(f"Error retrieving user {user_hash}: {str(e)}")
            raise InvalidUserError("Failed to retrieve user", user_id=user_hash)
    
    @staticmethod
    def update_user_last_login(user: User) -> None:
        """
        Update user's last login timestamp.
        
        Args:
            user: User instance to update
        """
        try:
            from django.utils import timezone
            user.last_login_at = timezone.now()
            user.save(update_fields=['last_login_at'])
            logger.debug(f"Updated last login for user: {user.username}")
            
        except Exception as e:
            logger.error(f"Failed to update last login for {user.username}: {str(e)}")
            # Don't raise exception as this is not critical
    
    @staticmethod
    def get_active_users_count() -> int:
        """Get count of active users."""
        try:
            return User.objects.filter(is_active=True).count()
        except Exception as e:
            logger.error(f"Error counting active users: {str(e)}")
            return 0
    
    @staticmethod
    def validate_user_role_permissions(user: User, required_role: str) -> bool:
        """
        Validate if user has required role permissions.
        
        Args:
            user: User instance
            required_role: Required role ('manager', 'admin')
            
        Returns:
            True if user has permission, False otherwise
        """
        role_hierarchy = {
            'employee': 1,
            'manager': 2,
            'admin': 3
        }
        
        user_level = role_hierarchy.get(user.role, 0)
        required_level = role_hierarchy.get(required_role, 999)
        
        return user_level >= required_level