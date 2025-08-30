"""
Centralized logging configuration for MindPulse application.
Provides structured logging with different levels and handlers.
"""
import logging
import logging.config
import sys
from pathlib import Path

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent.parent / 'logs'
LOGS_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'simple',
        },
        'console_debug': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'mindpulse.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'errors.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'analytics_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'analytics.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 3,
            'formatter': 'json',
        },
        'celery_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'celery.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 3,
            'formatter': 'verbose',
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'filters': ['require_debug_false'],
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['error_file', 'mail_admins'],
            'level': 'WARNING',
            'propagate': False,
        },
        'core': {
            'handlers': ['console', 'file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'core.services.analytics_service': {
            'handlers': ['analytics_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'core.tasks': {
            'handlers': ['celery_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['celery_file', 'console'],
            'level': 'INFO',
            'propagate': False,
        },
        'transformers': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'urllib3': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file'],
    },
}


def setup_logging():
    """Apply logging configuration."""
    logging.config.dictConfig(LOGGING_CONFIG)
    
    # Add custom log levels
    logging.addLevelName(25, "SUCCESS")
    logging.addLevelName(35, "BUSINESS")
    
    def success(self, message, *args, **kwargs):
        if self.isEnabledFor(25):
            self._log(25, message, args, **kwargs)
    
    def business(self, message, *args, **kwargs):
        if self.isEnabledFor(35):
            self._log(35, message, args, **kwargs)
    
    logging.Logger.success = success
    logging.Logger.business = business


class PerformanceLogger:
    """Context manager for performance logging."""
    
    def __init__(self, operation_name: str, logger: logging.Logger = None):
        self.operation_name = operation_name
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.time()
        self.logger.info(f"Starting operation: {self.operation_name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration = time.time() - self.start_time
        
        if exc_type:
            self.logger.error(
                f"Operation failed: {self.operation_name} after {duration:.2f}s",
                exc_info=(exc_type, exc_val, exc_tb)
            )
        else:
            self.logger.info(f"Operation completed: {self.operation_name} in {duration:.2f}s")


class BusinessEventLogger:
    """Logger for business events and metrics."""
    
    def __init__(self):
        self.logger = logging.getLogger('core.business')
    
    def log_user_activity(self, user_id: str, action: str, details: dict = None):
        """Log user activity events."""
        self.logger.info(
            f"User Activity: {action}",
            extra={
                'user_id': user_id,
                'action': action,
                'details': details or {},
                'event_type': 'user_activity'
            }
        )
    
    def log_analytics_query(self, query_type: str, parameters: dict, duration: float):
        """Log analytics query performance."""
        self.logger.info(
            f"Analytics Query: {query_type}",
            extra={
                'query_type': query_type,
                'parameters': parameters,
                'duration_seconds': duration,
                'event_type': 'analytics_query'
            }
        )
    
    def log_ml_processing(self, message_id: str, processing_time: float, results: dict):
        """Log ML processing events."""
        self.logger.info(
            f"ML Processing completed for message {message_id}",
            extra={
                'message_id': message_id,
                'processing_time': processing_time,
                'results': results,
                'event_type': 'ml_processing'
            }
        )
    
    def log_wellbeing_alert(self, alert_type: str, severity: str, affected_users: int):
        """Log wellbeing alerts."""
        self.logger.warning(
            f"Wellbeing Alert: {alert_type}",
            extra={
                'alert_type': alert_type,
                'severity': severity,
                'affected_users': affected_users,
                'event_type': 'wellbeing_alert'
            }
        )