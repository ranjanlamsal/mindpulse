import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class MindPulseException(Exception):
    """Base exception for MindPulse application with enhanced error tracking."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = 400,
        error_code: str = None,
        details: Dict[str, Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__
        self.details = details or {}
        
        # Log the exception for monitoring
        logger.error(
            f"{self.error_code}: {message}",
            extra={'status_code': status_code, 'details': details}
        )
        
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary for API responses."""
        return {
            'message': self.message,
            'error_code': self.error_code,
            'details': self.details
        }


class ValidationError(MindPulseException):
    """Raised for input validation failures."""
    def __init__(self, message: str = "Validation failed", field: str = None):
        details = {'field': field} if field else {}
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR", details=details)


class UserConsentError(MindPulseException):
    """Raised when user lacks data processing consent."""
    def __init__(self, message: str = "User has not consented to data processing"):
        super().__init__(message, status_code=403, error_code="USER_CONSENT_REQUIRED")


class InvalidChannelError(MindPulseException):
    """Raised when channel is invalid or inactive."""
    def __init__(self, message: str = "Invalid or inactive channel", channel_id: str = None):
        details = {'channel_id': channel_id} if channel_id else {}
        super().__init__(message, status_code=400, error_code="INVALID_CHANNEL", details=details)


class InvalidThreadError(MindPulseException):
    """Raised when Thread is invalid or inactive."""
    def __init__(self, message: str = "Invalid or inactive Thread", thread_id: str = None):
        details = {'thread_id': thread_id} if thread_id else {}
        super().__init__(message, status_code=400, error_code="INVALID_THREAD", details=details)


class InvalidUserError(MindPulseException):
    """Raised when user is invalid or not found."""
    def __init__(self, message: str = "Invalid user", user_id: str = None):
        details = {'user_id': user_id} if user_id else {}
        super().__init__(message, status_code=404, error_code="INVALID_USER", details=details)


class MessageProcessingError(MindPulseException):
    """Raised when message processing (e.g., NLP) fails."""
    def __init__(self, message: str = "Failed to process message", message_id: str = None):
        details = {'message_id': message_id} if message_id else {}
        super().__init__(message, status_code=500, error_code="MESSAGE_PROCESSING_ERROR", details=details)


class AggregationError(MindPulseException):
    """Raised when well-being aggregation fails."""
    def __init__(self, message: str = "Failed to aggregate well-being data", aggregation_type: str = None):
        details = {'aggregation_type': aggregation_type} if aggregation_type else {}
        super().__init__(message, status_code=500, error_code="AGGREGATION_ERROR", details=details)


class AuthenticationError(MindPulseException):
    """Raised for authentication failures."""
    def __init__(self, message: str = "Invalid credentials", username: str = None):
        details = {'username': username} if username else {}
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR", details=details)


class AuthorizationError(MindPulseException):
    """Raised for authorization failures."""
    def __init__(self, message: str = "Unauthorized access", required_role: str = None):
        details = {'required_role': required_role} if required_role else {}
        super().__init__(message, status_code=403, error_code="AUTHORIZATION_ERROR", details=details)


class RateLimitError(MindPulseException):
    """Raised when rate limit is exceeded."""
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = None):
        details = {'retry_after_seconds': retry_after} if retry_after else {}
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_EXCEEDED", details=details)


class DataIntegrityError(MindPulseException):
    """Raised for data integrity violations."""
    def __init__(self, message: str = "Data integrity violation", constraint: str = None):
        details = {'constraint': constraint} if constraint else {}
        super().__init__(message, status_code=409, error_code="DATA_INTEGRITY_ERROR", details=details)


class ExternalServiceError(MindPulseException):
    """Raised when external service calls fail."""
    def __init__(self, message: str = "External service unavailable", service: str = None):
        details = {'service': service} if service else {}
        super().__init__(message, status_code=503, error_code="EXTERNAL_SERVICE_ERROR", details=details)


class ConfigurationError(MindPulseException):
    """Raised for configuration-related errors."""
    def __init__(self, message: str = "Configuration error", setting: str = None):
        details = {'setting': setting} if setting else {}
        super().__init__(message, status_code=500, error_code="CONFIGURATION_ERROR", details=details)