"""
Standardized response builder for consistent API responses.
Follows DRY principles and provides unified error handling.
"""
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from typing import Any, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)


class APIResponseBuilder:
    """Centralized response builder for consistent API responses."""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = None,
        status_code: int = status.HTTP_200_OK,
        meta: Dict[str, Any] = None
    ) -> Response:
        """Build successful response."""
        response_data = {}
        
        if data is not None:
            response_data['data'] = data
            
        if message:
            response_data['message'] = message
            
        if meta:
            response_data['meta'] = meta
            
        response_data['timestamp'] = timezone.now().isoformat()
        response_data['success'] = True
        
        return Response(response_data, status=status_code)
    
    @staticmethod
    def error(
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        errors: Dict[str, List[str]] = None,
        error_code: str = None
    ) -> Response:
        """Build error response."""
        response_data = {
            'success': False,
            'message': message,
            'timestamp': timezone.now().isoformat()
        }
        
        if errors:
            response_data['errors'] = errors
            
        if error_code:
            response_data['error_code'] = error_code
            
        logger.error(f"API Error: {message} (Status: {status_code})")
        return Response(response_data, status=status_code)
    
    @staticmethod
    def validation_error(
        message: str = "Validation failed",
        errors: Dict[str, List[str]] = None
    ) -> Response:
        """Build validation error response."""
        return APIResponseBuilder.error(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            errors=errors,
            error_code="VALIDATION_ERROR"
        )
    
    @staticmethod
    def not_found(message: str = "Resource not found") -> Response:
        """Build not found error response."""
        return APIResponseBuilder.error(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND"
        )
    
    @staticmethod
    def unauthorized(message: str = "Authentication required") -> Response:
        """Build unauthorized error response."""
        return APIResponseBuilder.error(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED"
        )
    
    @staticmethod
    def forbidden(message: str = "Insufficient permissions") -> Response:
        """Build forbidden error response."""
        return APIResponseBuilder.error(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="FORBIDDEN"
        )
    
    @staticmethod
    def internal_error(
        message: str = "Internal server error",
        error_details: str = None
    ) -> Response:
        """Build internal server error response."""
        if error_details:
            logger.error(f"Internal Error Details: {error_details}")
            
        return APIResponseBuilder.error(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="INTERNAL_ERROR"
        )
    
    @staticmethod
    def paginated_success(
        data: List[Any],
        page: int,
        page_size: int,
        total_count: int,
        message: str = None
    ) -> Response:
        """Build paginated success response."""
        total_pages = (total_count + page_size - 1) // page_size
        
        meta = {
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_previous': page > 1
            }
        }
        
        return APIResponseBuilder.success(
            data=data,
            message=message,
            meta=meta
        )


# Convenience functions for common use cases
def success_response(data=None, message=None, status_code=status.HTTP_200_OK):
    """Convenience function for success response."""
    return APIResponseBuilder.success(data, message, status_code)

def error_response(message, status_code=status.HTTP_400_BAD_REQUEST):
    """Convenience function for error response."""
    return APIResponseBuilder.error(message, status_code)

def created_response(data=None, message="Created successfully"):
    """Convenience function for created response."""
    return APIResponseBuilder.success(data, message, status.HTTP_201_CREATED)

def updated_response(data=None, message="Updated successfully"):
    """Convenience function for updated response."""
    return APIResponseBuilder.success(data, message, status.HTTP_200_OK)

def deleted_response(message="Deleted successfully"):
    """Convenience function for deleted response."""
    return APIResponseBuilder.success(None, message, status.HTTP_204_NO_CONTENT)