"""
Analytics service for wellbeing data processing.
Separated business logic from views for better maintainability.
"""
from datetime import datetime, timezone, timedelta
from core.models.user_model import User
from core.models.channel_model import WellbeingAggregate, Channel
from core.models.message_model import MessageAnalysis, Message
from core.exceptions import AggregationError, ValidationError
from django.db.models import Avg, Sum, Count, Q, QuerySet
from django.utils import timezone as django_timezone
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class WellbeingMetrics:
    """Data class for wellbeing metrics."""
    sentiment_avg: float
    stress_avg: float
    emotions: Dict[str, float]
    message_count: int
    wellbeing_score: float
    alert_level: str = "normal"
    trend: str = "stable"


@dataclass
class DateRange:
    """Data class for date range operations."""
    start_date: datetime
    end_date: datetime
    
    @property
    def previous_range(self) -> 'DateRange':
        """Get previous period of same duration."""
        duration = self.end_date - self.start_date
        return DateRange(
            start_date=self.start_date - duration,
            end_date=self.start_date
        )


class AnalyticsService:
    """Service class for analytics operations with optimized queries."""
    
    @staticmethod
    def get_default_date_range(days: int = 30) -> DateRange:
        """Get default date range."""
        end_date = django_timezone.now()
        start_date = end_date - timedelta(days=days)
        return DateRange(start_date, end_date)

def calculate_wellbeing_score(sentiment_avg, stress_avg, emotions):
    """Calculate a 0-10 wellbeing score based on metrics."""
    base_score = 5.0
    
    # Sentiment impact (-2 to +2)
    sentiment_impact = sentiment_avg * 2.0 if sentiment_avg else 0
    
    # Stress impact (-1.5 to 0)
    stress_impact = -stress_avg * 1.5 if stress_avg else 0
    
    # Emotion boosts and penalties
    joy_boost = emotions.get('joy', 0) * 1.0
    love_boost = emotions.get('love', 0) * 0.8
    surprise_boost = emotions.get('surprise', 0) * 0.3
    
    sadness_penalty = -emotions.get('sadness', 0) * 1.2
    anger_penalty = -emotions.get('anger', 0) * 1.5
    fear_penalty = -emotions.get('fear', 0) * 1.0
    
    final_score = (base_score + sentiment_impact + stress_impact + 
                  joy_boost + love_boost + surprise_boost + 
                  sadness_penalty + anger_penalty + fear_penalty)
    
    return max(0, min(10, round(final_score, 1)))

def get_trend_indicator(current_score, previous_score):
    """Determine trend based on score comparison."""
    if previous_score == 0:
        return "new"
    
    change_percent = ((current_score - previous_score) / previous_score) * 100
    
    if change_percent > 5:
        return "improving"
    elif change_percent < -5:
        return "declining"
    else:
        return "stable"

def get_alert_level(wellbeing_score, stress_avg):
    """Determine alert level based on metrics."""
    if wellbeing_score < 3 or stress_avg > 0.7:
        return "critical"
    elif wellbeing_score < 5 or stress_avg > 0.5:
        return "warning"
    elif wellbeing_score > 7 and stress_avg < 0.2:
        return "excellent"
    else:
        return "normal"

def format_emotions_data(emotions_raw):
    """Format emotions data for frontend consumption."""
    return {
        "joy": float(emotions_raw.get('joy', 0)),
        "sadness": float(emotions_raw.get('sadness', 0)),
        "anger": float(emotions_raw.get('anger', 0)),
        "fear": float(emotions_raw.get('fear', 0)),
        "love": float(emotions_raw.get('love', 0)),
        "surprise": float(emotions_raw.get('surprise', 0))
    }

def get_team_analytics(start_date=None, end_date=None):
    """Get comprehensive team analytics for management dashboard."""
    # Default to last 30 days if no dates provided
    end_date = end_date or django_timezone.now()
    start_date = start_date or (end_date - timedelta(days=30))
    
    # Get previous period for trend comparison
    prev_end = start_date
    prev_start = prev_end - (end_date - start_date)
    
    result = {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "calculated_at": django_timezone.now().isoformat()
        },
        "team_overview": {},
        "user_analytics": [],
        "channel_analytics": [],
        "trends": {},
        "alerts": []
    }
    
    # Team Overview
    team_data = WellbeingAggregate.objects.filter(
        user_hash__isnull=True,
        source='overall',
        period_start__gte=start_date,
        period_end__lte=end_date
    ).aggregate(
        sentiment_avg=Avg('sentiment_weighted_avg') or 0.0,
        stress_avg=Avg('stress_weighted_avg') or 0.0,
        joy_avg=Avg('emotion_joy_avg') or 0.0,
        sadness_avg=Avg('emotion_sadness_avg') or 0.0,
        anger_avg=Avg('emotion_anger_avg') or 0.0,
        fear_avg=Avg('emotion_fear_avg') or 0.0,
        love_avg=Avg('emotion_love_avg') or 0.0,
        surprise_avg=Avg('emotion_surprise_avg') or 0.0,
        total_messages=Sum('message_count') or 0
    )
    
    emotions_data = format_emotions_data({
        'joy': team_data['joy_avg'],
        'sadness': team_data['sadness_avg'],
        'anger': team_data['anger_avg'],
        'fear': team_data['fear_avg'],
        'love': team_data['love_avg'],
        'surprise': team_data['surprise_avg']
    })
    
    wellbeing_score = calculate_wellbeing_score(
        team_data['sentiment_avg'],
        team_data['stress_avg'],
        emotions_data
    )
    
    result["team_overview"] = {
        "sentiment_weighted_avg": float(team_data['sentiment_avg']),
        "stress_weighted_avg": float(team_data['stress_avg']),
        "emotions": emotions_data,
        "message_count": team_data['total_messages'],
        "wellbeing_score": wellbeing_score,
        "alert_level": get_alert_level(wellbeing_score, team_data['stress_avg'])
    }
    
    # User Analytics (anonymized)
    user_aggregates = WellbeingAggregate.objects.filter(
        user_hash__isnull=False,
        source='overall',
        period_start__gte=start_date,
        period_end__lte=end_date
    ).values('user_hash').annotate(
        sentiment_avg=Avg('sentiment_weighted_avg'),
        stress_avg=Avg('stress_weighted_avg'),
        joy_avg=Avg('emotion_joy_avg'),
        sadness_avg=Avg('emotion_sadness_avg'),
        anger_avg=Avg('emotion_anger_avg'),
        fear_avg=Avg('emotion_fear_avg'),
        love_avg=Avg('emotion_love_avg'),
        surprise_avg=Avg('emotion_surprise_avg'),
        total_messages=Sum('message_count')
    ).order_by('user_hash')
    
    for i, user_data in enumerate(user_aggregates):
        emotions = format_emotions_data({
            'joy': user_data['joy_avg'],
            'sadness': user_data['sadness_avg'],
            'anger': user_data['anger_avg'],
            'fear': user_data['fear_avg'],
            'love': user_data['love_avg'],
            'surprise': user_data['surprise_avg']
        })
        
        wellbeing_score = calculate_wellbeing_score(
            user_data['sentiment_avg'],
            user_data['stress_avg'],
            emotions
        )
        
        # Get previous period data for trend
        prev_user_data = WellbeingAggregate.objects.filter(
            user_hash=user_data['user_hash'],
            source='overall',
            period_start__gte=prev_start,
            period_end__lte=prev_end
        ).aggregate(
            prev_sentiment=Avg('sentiment_weighted_avg'),
            prev_stress=Avg('stress_weighted_avg'),
            prev_joy=Avg('emotion_joy_avg'),
            prev_sadness=Avg('emotion_sadness_avg'),
            prev_anger=Avg('emotion_anger_avg'),
            prev_fear=Avg('emotion_fear_avg'),
            prev_love=Avg('emotion_love_avg'),
            prev_surprise=Avg('emotion_surprise_avg')
        )
        
        prev_emotions = format_emotions_data({
            'joy': prev_user_data.get('prev_joy', 0),
            'sadness': prev_user_data.get('prev_sadness', 0),
            'anger': prev_user_data.get('prev_anger', 0),
            'fear': prev_user_data.get('prev_fear', 0),
            'love': prev_user_data.get('prev_love', 0),
            'surprise': prev_user_data.get('prev_surprise', 0)
        })
        
        prev_wellbeing_score = calculate_wellbeing_score(
            prev_user_data.get('prev_sentiment', 0),
            prev_user_data.get('prev_stress', 0),
            prev_emotions
        )
        
        result["user_analytics"].append({
            "user_id": f"user_{i+1:03d}",  # Anonymized ID
            "sentiment_weighted_avg": float(user_data['sentiment_avg'] or 0),
            "stress_weighted_avg": float(user_data['stress_avg'] or 0),
            "emotions": emotions,
            "message_count": user_data['total_messages'] or 0,
            "wellbeing_score": wellbeing_score,
            "trend": get_trend_indicator(wellbeing_score, prev_wellbeing_score),
            "alert_level": get_alert_level(wellbeing_score, user_data['stress_avg'] or 0)
        })
    
    # Channel Analytics
    channel_aggregates = WellbeingAggregate.objects.filter(
        user_hash__isnull=False,
        source__in=['discord', 'meeting', 'jira', 'chat'],
        period_start__gte=start_date,
        period_end__lte=end_date
    ).values('source').annotate(
        sentiment_avg=Avg('sentiment_weighted_avg'),
        stress_avg=Avg('stress_weighted_avg'),
        joy_avg=Avg('emotion_joy_avg'),
        sadness_avg=Avg('emotion_sadness_avg'),
        anger_avg=Avg('emotion_anger_avg'),
        fear_avg=Avg('emotion_fear_avg'),
        love_avg=Avg('emotion_love_avg'),
        surprise_avg=Avg('emotion_surprise_avg'),
        total_messages=Sum('message_count'),
        active_users=Count('user_hash', distinct=True)
    ).order_by('source')
    
    for channel_data in channel_aggregates:
        emotions = format_emotions_data({
            'joy': channel_data['joy_avg'],
            'sadness': channel_data['sadness_avg'],
            'anger': channel_data['anger_avg'],
            'fear': channel_data['fear_avg'],
            'love': channel_data['love_avg'],
            'surprise': channel_data['surprise_avg']
        })
        
        wellbeing_score = calculate_wellbeing_score(
            channel_data['sentiment_avg'],
            channel_data['stress_avg'],
            emotions
        )
        
        result["channel_analytics"].append({
            "source": channel_data['source'],
            "sentiment_weighted_avg": float(channel_data['sentiment_avg'] or 0),
            "stress_weighted_avg": float(channel_data['stress_avg'] or 0),
            "emotions": emotions,
            "message_count": channel_data['total_messages'] or 0,
            "active_users": channel_data['active_users'],
            "wellbeing_score": wellbeing_score,
            "alert_level": get_alert_level(wellbeing_score, channel_data['stress_avg'] or 0)
        })
    
    # Generate Alerts
    alerts = []
    
    # Critical wellbeing users
    critical_users = [u for u in result["user_analytics"] if u["alert_level"] == "critical"]
    if critical_users:
        alerts.append({
            "type": "critical_wellbeing",
            "severity": "high",
            "message": f"{len(critical_users)} employees showing critical wellbeing indicators",
            "count": len(critical_users),
            "action_required": True
        })
    
    # High stress users
    warning_users = [u for u in result["user_analytics"] if u["alert_level"] == "warning"]
    if warning_users:
        alerts.append({
            "type": "elevated_stress",
            "severity": "medium",
            "message": f"{len(warning_users)} employees showing elevated stress levels",
            "count": len(warning_users),
            "action_required": False
        })
    
    # Channel performance issues
    poor_channels = [c for c in result["channel_analytics"] if c["wellbeing_score"] < 4]
    if poor_channels:
        alerts.append({
            "type": "channel_performance",
            "severity": "medium", 
            "message": f"Poor wellbeing indicators in {', '.join([c['source'] for c in poor_channels])}",
            "count": len(poor_channels),
            "action_required": False
        })
    
    result["alerts"] = alerts
    
    return result