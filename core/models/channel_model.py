"""
Optimized Channel model with proper constraints and enhanced indexing.
"""
from django.db import models
from core.models.base_model import AbstractBaseModel


class Channel(AbstractBaseModel):
    """Optimized Channel model with proper constraints and indexing."""
    
    name = models.CharField(max_length=100, db_index=True)  # Add index for searches
    type = models.CharField(
        max_length=50,
        choices=[
            ('jira', 'Jira'), 
            ('chat', 'Chat'), 
            ('meeting', 'Meeting'), 
            ('discord', 'Discord')
        ],
        db_index=True  # Index for type-based queries
    )
    external_id = models.CharField(max_length=50, db_index=True)  # Index for lookups
    is_active = models.BooleanField(default=True, db_index=True)  # Index for active queries
    
    class Meta:
        # Critical: Add unique constraint for external_id + type
        unique_together = ('type', 'external_id')
        indexes = [
            # Composite indexes for common query patterns
            models.Index(fields=['type', 'is_active']),
            models.Index(fields=['external_id', 'type']),
            models.Index(fields=['name', 'type']),
            models.Index(fields=['is_active', 'created_at']),
        ]
        # Optimize table for read-heavy workload
        db_table_comment = "Channel information with optimized indexing for analytics queries"

    def __str__(self):
        return f"{self.name} ({self.type})"

    @classmethod
    def get_or_create_channel_instance(cls, name, type, external_id):
        channel, created = cls.objects.get_or_create(
            type=type,
            external_id=external_id,
            defaults={"name": name}
        )

        if not created and channel.name != name:
            channel.name = name
            channel.save(update_fields=["name"])
        return channel, created


class WellbeingIndex(AbstractBaseModel):
    user_hash = models.UUIDField(db_index=True)
    source = models.ForeignKey(Channel, on_delete=models.CASCADE)
    sentiment_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    stress_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    emotion_avg = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    class Meta:
        unique_together = ('user_hash', 'source', 'period_start')
        indexes = [
            models.Index(fields=['user_hash', 'source', 'period_start']),
        ]

class WellbeingAggregate(AbstractBaseModel):
    """Optimized WellbeingAggregate with enhanced indexing for dashboard queries."""
    
    user_hash = models.UUIDField(db_index=True, null=True, blank=True)
    source = models.CharField(
        max_length=50, 
        null=True, 
        blank=True,
        choices=[
            ('overall', 'Overall'),
            ('discord', 'Discord'),
            ('jira', 'Jira'),
            ('chat', 'Chat'),
            ('meeting', 'Meeting')
        ],
        db_index=True
    )
    
    # Enhanced time period fields with indexes
    period_start = models.DateTimeField(db_index=True)
    period_end = models.DateTimeField(db_index=True)
    period_type = models.CharField(
        max_length=20,
        choices=[
            ('hourly', 'Hourly'),
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly')
        ],
        default='daily',
        db_index=True
    )
    
    # Metric fields with proper precision and indexes
    sentiment_weighted_avg = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000, db_index=True)
    stress_weighted_avg = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000, db_index=True)
    
    # Emotion averages with indexes for filtering
    emotion_sadness_avg = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000)
    emotion_joy_avg = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000, db_index=True)
    emotion_love_avg = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000)
    emotion_anger_avg = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000, db_index=True)
    emotion_fear_avg = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000)
    emotion_surprise_avg = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000)
    
    # Count and activity metrics
    message_count = models.PositiveIntegerField(default=0, db_index=True)
    active_users = models.PositiveIntegerField(default=0, db_index=True)
    
    # Calculated wellbeing score for fast queries
    wellbeing_score = models.DecimalField(max_digits=4, decimal_places=2, default=5.00, db_index=True)
    
    # Data quality indicators
    data_quality = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low')
        ],
        default='medium',
        db_index=True
    )

    class Meta:
        unique_together = ('user_hash', 'source', 'period_start', 'period_type')
        indexes = [
            # Critical: Dashboard query optimizations
            models.Index(fields=['user_hash', 'period_start', 'period_type']),
            models.Index(fields=['source', 'period_start', 'period_type']),
            models.Index(fields=['period_start', 'period_type', 'source']),
            
            # Team vs individual queries
            models.Index(fields=['user_hash', 'source', 'period_start']),
            models.Index(fields=['-user_hash', 'period_start']),  # Team aggregates (null user_hash)
            
            # Metric-based queries
            models.Index(fields=['wellbeing_score', 'period_start']),
            models.Index(fields=['sentiment_weighted_avg', 'period_start']),
            models.Index(fields=['stress_weighted_avg', 'period_start']),
            
            # Alert-based queries
            models.Index(fields=['wellbeing_score', 'source', 'period_start']),
            models.Index(fields=['stress_weighted_avg', 'user_hash']),
            
            # Data quality queries
            models.Index(fields=['data_quality', 'period_start']),
            models.Index(fields=['message_count', 'period_start']),
        ]
        
        # PostgreSQL specific optimizations
        db_table_comment = "Wellbeing aggregates with comprehensive indexing for analytics dashboard"

    def __str__(self):
        return f"Aggregate for {self.user_hash or 'team'} ({self.source or 'overall'}) - {self.period_start.date()}"
    