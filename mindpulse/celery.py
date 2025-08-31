"""
Simple Celery configuration for MindPulse.
"""
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindpulse.settings')

app = Celery('mindpulse')

# Load configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks automatically
app.autodiscover_tasks()

# Beat schedule for periodic tasks
app.conf.beat_schedule = {
    'aggregate-wellbeing-every-30-minutes': {
        'task': 'core.tasks.aggregation_tasks.aggregate_wellbeing',
        'schedule': crontab(minute='*/30'),
    },
}

app.conf.timezone = 'UTC'
