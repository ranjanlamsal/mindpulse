"""
Maintenance and monitoring tasks for system health.
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from core.models.message_model import Message, MessageAnalysis
from core.models.channel_model import WellbeingAggregate
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def cleanup_old_results(self):
    """
    Clean up old data to maintain database performance.
    Removes data older than configured retention periods.
    """
    try:
        current_time = timezone.now()
        
        # Clean up old message analyses (keep 90 days)
        message_cutoff = current_time - timedelta(days=90)
        old_analyses = MessageAnalysis.objects.filter(created_at__lt=message_cutoff)
        analyses_count = old_analyses.count()
        
        if analyses_count > 0:
            old_analyses.delete()
            logger.info(f"Cleaned up {analyses_count} old message analyses")
        
        # Clean up old aggregation data (keep 1 year)
        aggregation_cutoff = current_time - timedelta(days=365)
        old_aggregations = WellbeingAggregate.objects.filter(created_at__lt=aggregation_cutoff)
        aggregations_count = old_aggregations.count()
        
        if aggregations_count > 0:
            old_aggregations.delete()
            logger.info(f"Cleaned up {aggregations_count} old wellbeing aggregations")
        
        # Clean up orphaned messages (messages without analysis after 24 hours)
        orphaned_cutoff = current_time - timedelta(hours=24)
        orphaned_messages = Message.objects.filter(
            created_at__lt=orphaned_cutoff
        ).exclude(
            id__in=MessageAnalysis.objects.values('message_id')
        )
        orphaned_count = orphaned_messages.count()
        
        if orphaned_count > 0:
            orphaned_messages.delete()
            logger.info(f"Cleaned up {orphaned_count} orphaned messages")
        
        return {
            'status': 'success',
            'cleaned_analyses': analyses_count,
            'cleaned_aggregations': aggregations_count,
            'cleaned_orphaned': orphaned_count,
            'timestamp': current_time.isoformat()
        }
        
    except Exception as e:
        logger.error(f"Cleanup task failed: {str(e)}")
        # Retry with exponential backoff
        raise self.retry(countdown=60 * (2 ** self.request.retries), exc=e)


@shared_task(bind=True)
def health_check(self):
    """
    System health check task.
    Monitors database connectivity and system performance.
    """
    try:
        from django.db import connection
        from django.core.cache import cache
        import psutil
        import time
        
        start_time = time.time()
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {}
        }
        
        # Database connectivity check
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            health_status['checks']['database'] = {'status': 'ok', 'response_time_ms': 0}
        except Exception as db_error:
            health_status['checks']['database'] = {
                'status': 'error', 
                'error': str(db_error)
            }
            health_status['status'] = 'degraded'
        
        # Cache connectivity check (if Redis is configured)
        try:
            cache.set('health_check', 'ok', 30)
            cache_result = cache.get('health_check')
            health_status['checks']['cache'] = {
                'status': 'ok' if cache_result == 'ok' else 'error'
            }
        except Exception as cache_error:
            health_status['checks']['cache'] = {
                'status': 'error',
                'error': str(cache_error)
            }
        
        # System resources check
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health_status['checks']['system'] = {
                'status': 'ok',
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'available_memory_gb': round(memory.available / (1024**3), 2),
                'available_disk_gb': round(disk.free / (1024**3), 2)
            }
            
            # Alert if resources are running low
            if memory.percent > 85 or disk.percent > 85:
                health_status['status'] = 'warning'
                logger.warning(f"System resources low - Memory: {memory.percent}%, Disk: {disk.percent}%")
                
        except ImportError:
            # psutil not installed
            health_status['checks']['system'] = {'status': 'skipped', 'reason': 'psutil not available'}
        except Exception as sys_error:
            health_status['checks']['system'] = {'status': 'error', 'error': str(sys_error)}
        
        # Model availability check
        try:
            from core.accessors.model_accessors import stress_classifier, emotion_classifier, sentiment_classifier
            
            # Quick test of model loading
            test_result = stress_classifier("test")
            health_status['checks']['ml_models'] = {'status': 'ok'}
            
        except Exception as ml_error:
            health_status['checks']['ml_models'] = {
                'status': 'error',
                'error': str(ml_error)
            }
            health_status['status'] = 'degraded'
        
        # Data quality check
        try:
            recent_messages = Message.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            recent_analyses = MessageAnalysis.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            health_status['checks']['data_processing'] = {
                'status': 'ok',
                'recent_messages': recent_messages,
                'recent_analyses': recent_analyses,
                'processing_ratio': round(recent_analyses / max(recent_messages, 1), 2)
            }
            
        except Exception as data_error:
            health_status['checks']['data_processing'] = {
                'status': 'error',
                'error': str(data_error)
            }
        
        # Overall response time
        health_status['response_time_ms'] = round((time.time() - start_time) * 1000, 2)
        
        logger.info(f"Health check completed: {health_status['status']}")
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }


@shared_task(bind=True, max_retries=2)
def optimize_database(self):
    """
    Optimize database performance by updating statistics and analyzing tables.
    """
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            # For SQLite, run ANALYZE to update query planner statistics
            if 'sqlite' in connection.vendor:
                cursor.execute("ANALYZE")
                logger.info("Database statistics updated (SQLite ANALYZE)")
                
            # For PostgreSQL
            elif 'postgresql' in connection.vendor:
                # Get all MindPulse tables
                cursor.execute("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public' AND tablename LIKE 'core_%'
                """)
                tables = cursor.fetchall()
                
                for (table,) in tables:
                    cursor.execute(f"ANALYZE {table}")
                
                logger.info(f"Database statistics updated for {len(tables)} tables")
        
        return {
            'status': 'success',
            'timestamp': timezone.now().isoformat(),
            'database_vendor': connection.vendor
        }
        
    except Exception as e:
        logger.error(f"Database optimization failed: {str(e)}")
        raise self.retry(countdown=300, exc=e)  # Retry after 5 minutes


@shared_task(bind=True)
def generate_system_report(self):
    """
    Generate comprehensive system report for monitoring.
    """
    try:
        from django.db.models import Count, Avg
        from datetime import datetime
        
        current_time = timezone.now()
        report = {
            'timestamp': current_time.isoformat(),
            'period': '24h',
            'metrics': {}
        }
        
        # Message processing metrics
        last_24h = current_time - timedelta(hours=24)
        
        message_stats = Message.objects.filter(created_at__gte=last_24h).aggregate(
            total_messages=Count('id'),
            channels=Count('channel', distinct=True)
        )
        
        analysis_stats = MessageAnalysis.objects.filter(created_at__gte=last_24h).aggregate(
            total_analyses=Count('id'),
            avg_sentiment=Avg('sentiment_score'),
            avg_stress=Avg('stress_score'),
            avg_emotion=Avg('emotion_score')
        )
        
        wellbeing_stats = WellbeingAggregate.objects.filter(created_at__gte=last_24h).aggregate(
            total_aggregates=Count('id'),
            active_users=Count('user_hash', distinct=True)
        )
        
        report['metrics'] = {
            'messages': message_stats,
            'analyses': analysis_stats,
            'wellbeing': wellbeing_stats,
            'processing_efficiency': {
                'analysis_rate': round(
                    analysis_stats['total_analyses'] / max(message_stats['total_messages'], 1), 2
                ),
                'messages_per_channel': round(
                    message_stats['total_messages'] / max(message_stats['channels'], 1), 2
                )
            }
        }
        
        logger.info("System report generated successfully")
        return report
        
    except Exception as e:
        logger.error(f"System report generation failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': timezone.now().isoformat()
        }