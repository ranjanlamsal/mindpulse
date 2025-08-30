"""
Optimized Message and MessageAnalysis models with enhanced indexing for analytics.
"""
from django.db import models
from core.models.channel_model import Channel
from core.models.base_model import AbstractBaseModel
from core.constants import (
    SENTIMENT_MAPPING,
    STRESS_MAPPING,
    EMOTION_MAPPING
)


class Message(AbstractBaseModel):
    """Optimized Message model with proper indexing for analytics queries."""
    
    channel = models.ForeignKey(
        Channel, 
        on_delete=models.CASCADE,
        db_index=True,
        related_name='messages'
    )
    user_hash = models.UUIDField(db_index=True)
    message = models.TextField()
    external_ref = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        db_index=True  # Index for external reference lookups
    )
    
    # Add message length for optimization
    message_length = models.PositiveIntegerField(default=0, db_index=True)
    
    # Add processing status for tracking
    processing_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending',
        db_index=True
    )

    class Meta:
        unique_together = ('channel', 'external_ref')
        indexes = [
            # Critical: Composite indexes for common analytics queries
            models.Index(fields=['user_hash', 'created_at']),
            models.Index(fields=['channel', 'user_hash', 'created_at']),
            models.Index(fields=['channel', 'created_at']),
            models.Index(fields=['processing_status', 'created_at']),
            models.Index(fields=['user_hash', 'channel']),
            models.Index(fields=['created_at', 'processing_status']),
            # For message length analysis
            models.Index(fields=['message_length', 'created_at']),
        ]
        # Partition hint for large tables (PostgreSQL)
        db_table_comment = "Messages with optimized indexing for wellbeing analytics"

    def save(self, *args, **kwargs):
        """Override save to calculate message length."""
        if self.message:
            self.message_length = len(self.message)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Message from {self.channel} at {self.created_at}"


class MessageAnalysis(AbstractBaseModel):
    """Optimized MessageAnalysis with proper indexing for aggregation queries."""
    
    message = models.OneToOneField(
        Message, 
        on_delete=models.CASCADE,
        related_name='analysis'
    )
    
    # Indexed sentiment fields for fast filtering
    sentiment = models.CharField(
        max_length=20,
        choices=[
            ('positive', 'Positive'),
            ('negative', 'Negative'),
            ('neutral', 'Neutral')
        ],
        db_index=True
    )
    sentiment_score = models.FloatField(db_index=True)

    # Indexed emotion fields for fast aggregation
    emotion = models.CharField(
        max_length=50,
        choices=[
            ('sadness', 'Sadness'),
            ('joy', 'Joy'),
            ('love', 'Love'),
            ('anger', 'Anger'),
            ('fear', 'Fear'),
            ('surprise', 'Surprise'),
            ('unknown', 'Unknown')
        ],
        db_index=True
    )
    emotion_score = models.FloatField(db_index=True)

    # Indexed stress fields
    stress = models.BooleanField(default=False, db_index=True)
    stress_score = models.FloatField(db_index=True)
    
    # Add confidence scores for ML models
    sentiment_confidence = models.FloatField(default=0.0)
    emotion_confidence = models.FloatField(default=0.0)
    stress_confidence = models.FloatField(default=0.0)

    class Meta:
        indexes = [
            # Critical: Indexes for wellbeing aggregation queries
            models.Index(fields=['sentiment', 'created_at']),
            models.Index(fields=['emotion', 'created_at']),
            models.Index(fields=['stress', 'created_at']),
            models.Index(fields=['sentiment_score', 'created_at']),
            models.Index(fields=['emotion_score', 'created_at']),
            models.Index(fields=['stress_score', 'created_at']),
            
            # Composite indexes for complex analytics
            models.Index(fields=['sentiment', 'emotion', 'created_at']),
            models.Index(fields=['stress', 'sentiment', 'created_at']),
            
            # Message relationship indexes
            models.Index(fields=['message', 'created_at']),
        ]
        db_table_comment = "Message analysis results with optimized indexing for aggregations"

    def __str__(self):
        return f"Analysis for message {self.message}"
    