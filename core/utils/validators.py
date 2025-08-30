"""
Input validation utilities for consistent data validation.
"""
from datetime import datetime
from dateutil.parser import isoparse
from django.utils import timezone
from typing import Optional, Tuple, Dict, Any
import uuid

class ValidationError(Exception):
    """Custom validation error with field-specific messages."""
    
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(message)


class DateValidator:
    """Date parsing and validation utilities."""
    
    @staticmethod
    def parse_iso_date(date_str: str, field_name: str = "date") -> datetime:
        """Parse ISO 8601 date string with validation."""
        if not date_str:
            return None
            
        try:
            parsed_date = isoparse(date_str)
            if parsed_date.tzinfo is None:
                parsed_date = parsed_date.replace(tzinfo=timezone.utc)
            return parsed_date
        except ValueError:
            raise ValidationError(
                f"Invalid date format for {field_name}. Use ISO 8601 format (e.g., 2025-08-30T00:00:00Z)",
                field=field_name
            )
    
    @staticmethod
    def parse_date_range(
        start_date_str: Optional[str],
        end_date_str: Optional[str],
        default_days: int = 30
    ) -> Tuple[datetime, datetime]:
        """Parse and validate date range with defaults."""
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=default_days)
        
        if start_date_str:
            start_date = DateValidator.parse_iso_date(start_date_str, "start_date")
            
        if end_date_str:
            end_date = DateValidator.parse_iso_date(end_date_str, "end_date")
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError(
                "start_date must be before end_date",
                field="date_range"
            )
        
        return start_date, end_date


class UUIDValidator:
    """UUID validation utilities."""
    
    @staticmethod
    def validate_uuid(uuid_str: str, field_name: str = "uuid") -> uuid.UUID:
        """Validate and return UUID object."""
        if not uuid_str:
            raise ValidationError(f"{field_name} is required", field=field_name)
        
        try:
            return uuid.UUID(uuid_str)
        except ValueError:
            raise ValidationError(
                f"Invalid {field_name} format",
                field=field_name
            )


class PaginationValidator:
    """Pagination parameter validation."""
    
    @staticmethod
    def validate_pagination(
        page: str = "1",
        page_size: str = "20",
        max_page_size: int = 100
    ) -> Tuple[int, int]:
        """Validate and return pagination parameters."""
        try:
            page_num = int(page)
            if page_num < 1:
                raise ValidationError("Page must be greater than 0", field="page")
        except ValueError:
            raise ValidationError("Invalid page number", field="page")
        
        try:
            size = int(page_size)
            if size < 1:
                raise ValidationError("Page size must be greater than 0", field="page_size")
            if size > max_page_size:
                raise ValidationError(f"Page size cannot exceed {max_page_size}", field="page_size")
        except ValueError:
            raise ValidationError("Invalid page size", field="page_size")
        
        return page_num, size


class ChannelValidator:
    """Channel-related validation."""
    
    VALID_CHANNEL_TYPES = ['discord', 'meeting', 'jira', 'chat']
    
    @staticmethod
    def validate_channel_type(channel_type: str) -> str:
        """Validate channel type."""
        if not channel_type:
            raise ValidationError("Channel type is required", field="channel_type")
        
        if channel_type not in ChannelValidator.VALID_CHANNEL_TYPES:
            raise ValidationError(
                f"Invalid channel type. Must be one of: {', '.join(ChannelValidator.VALID_CHANNEL_TYPES)}",
                field="channel_type"
            )
        
        return channel_type


class MessageValidator:
    """Message content validation."""
    
    @staticmethod
    def validate_message_content(content: str) -> str:
        """Validate message content."""
        if not content or not content.strip():
            raise ValidationError("Message content cannot be empty", field="message")
        
        # Basic length validation
        if len(content) > 10000:  # 10KB max
            raise ValidationError("Message content too long (max 10,000 characters)", field="message")
        
        # Check for potentially malicious content
        dangerous_patterns = ['<script', 'javascript:', 'data:text/html']
        content_lower = content.lower()
        for pattern in dangerous_patterns:
            if pattern in content_lower:
                raise ValidationError("Message contains potentially unsafe content", field="message")
        
        return content.strip()


def validate_request_data(request_data: Dict[str, Any], required_fields: list) -> Dict[str, str]:
    """Validate required fields in request data."""
    errors = {}
    
    for field in required_fields:
        if field not in request_data or not request_data[field]:
            errors[field] = [f"{field} is required"]
    
    if errors:
        raise ValidationError("Required fields missing", field="validation")
    
    return request_data