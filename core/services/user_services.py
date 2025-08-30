from core.models.channel_model import Channel
from core.exceptions import (
    MindPulseException, 
    AuthenticationError
)
import logging
from core.models.user_model import User
from django.contrib.auth import authenticate
from datetime import datetime


logger = logging.getLogger(__name__)


def signup_user(validated_data):
    """Create a new user with validated data."""
    try:
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            role=validated_data.get("role", "employee"),
        )
        return user
    except Exception as e:
        logger.error(f"User signup failed: {e}")
        raise MindPulseException(f"Failed to create user: {str(e)}")


def login_user(username, password):
    """Authenticate and return user."""
    user = authenticate(username=username, password=password)
    if not user:
        raise AuthenticationError("Invalid credentials")
    if not user.is_active:
        raise AuthenticationError("User account is inactive")
    user.last_login_at = datetime.now()
    user.save()
    return user
