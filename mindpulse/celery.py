"""
Optimized Celery configuration for MindPulse.
Includes proper error handling, monitoring, and task scheduling.
"""
import os
from celery import Celery, signals
from celery.schedules import crontab
from celery.utils.log import get_task_logger
import logging

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindpulse.settings')

# Create Celery app with optimized configuration
app = Celery('mindpulse')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks automatically
app.autodiscover_tasks()

# Optimized Celery configuration
app.conf.update(
    # Task execution settings
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_reject_on_worker_lost=True,
    
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_compression='gzip',
    
    # Task routing
    task_routes={
        'core.tasks.message_analysis_tasks.process_message_analysis': {'queue': 'ml_processing'},
        'core.tasks.aggregation_tasks.aggregate_wellbeing': {'queue': 'aggregation'},
    },
    
    # Worker settings
    worker_max_tasks_per_child=1000,
    worker_disable_rate_limits=True,
    
    # Monitoring
    worker_send_task_events=True,
    task_send_sent_event=True,
)

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'aggregate-wellbeing-every-30-minutes': {
        'task': 'core.tasks.aggregation_tasks.aggregate_wellbeing',
        'schedule': crontab(minute='*/30'),
        'options': {'queue': 'aggregation'},
    },
    'cleanup-old-results': {
        'task': 'core.tasks.maintenance_tasks.cleanup_old_results',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
        'options': {'queue': 'maintenance'},
    },
    'health-check': {
        'task': 'core.tasks.maintenance_tasks.health_check',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
        'options': {'queue': 'monitoring'},
    },
}

app.conf.timezone = 'UTC'

# Task logging setup
logger = get_task_logger(__name__)

@signals.setup_logging.connect
def setup_celery_logging(**kwargs):
    """Setup logging for Celery workers."""
    from core.utils.logging_config import setup_logging
    setup_logging()

@signals.task_prerun.connect
def task_prerun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, **kwds):
    """Log task start."""
    logger.info(f'Starting task {task.name} with ID {task_id}')

@signals.task_postrun.connect
def task_postrun_handler(sender=None, task_id=None, task=None, args=None, kwargs=None, retval=None, state=None, **kwds):
    """Log task completion."""
    logger.info(f'Task {task.name} with ID {task_id} completed with state {state}')

@signals.task_failure.connect
def task_failure_handler(sender=None, task_id=None, exception=None, traceback=None, einfo=None, **kwds):
    """Log task failures."""
    logger.error(f'Task {sender.name} with ID {task_id} failed: {exception}')

@signals.task_retry.connect
def task_retry_handler(sender=None, task_id=None, reason=None, einfo=None, **kwds):
    """Log task retries."""
    logger.warning(f'Task {sender.name} with ID {task_id} retrying: {reason}')

# Health check task
@app.task(bind=True, name='celery.ping')
def ping(self):
    """Celery health check task."""
    return {'status': 'ok', 'worker': self.request.hostname}
