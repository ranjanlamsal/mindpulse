from datetime import datetime, timezone
from core.models.user_model import User
from core.models.channel_model import WellbeingAggregate
from django.db.models import Avg, Sum
from core.exceptions import (
    AuthorizationError
)
import logging
from datetime import timedelta
from core.exceptions import MindPulseException


logger = logging.getLogger(__name__)

def get_team_wellbeing(user, start_date=None, end_date=None):
    """Retrieve aggregated team, user, and channel well-being data for managers over a date range."""
    if user.role != 'manager':
        raise AuthorizationError("Only managers can access team data")

    try:
        # Default to last 30 days if no dates provided
        end_date = end_date or timezone.now()
        start_date = start_date or (end_date - timedelta(days=30))

        # Team aggregates
        team_data = WellbeingAggregate.objects.filter(
            user_hash__isnull=True,
            source='overall',
            period_start__gte=start_date,
            period_end__lte=end_date
        ).aggregate(
            sentiment_avg=Avg('sentiment_weighted_avg') or 0.0,
            stress_avg=Avg('stress_weighted_avg') or 0.0,
            sadness_avg=Avg('emotion_sadness_avg') or 0.0,
            joy_avg=Avg('emotion_joy_avg') or 0.0,
            love_avg=Avg('emotion_love_avg') or 0.0,
            anger_avg=Avg('emotion_anger_avg') or 0.0,
            fear_avg=Avg('emotion_fear_avg') or 0.0,
            surprise_avg=Avg('emotion_surprise_avg') or 0.0,
            total_messages=Sum('message_count') or 0
        )

        team_results = {
            "period_start": start_date,
            "period_end": end_date,
            "sentiment_weighted_avg": float(team_data['sentiment_avg']),
            "stress_weighted_avg": float(team_data['stress_avg']),
            "emotions": {
                "sadness": float(team_data['sadness_avg']),
                "joy": float(team_data['joy_avg']),
                "love": float(team_data['love_avg']),
                "anger": float(team_data['anger_avg']),
                "fear": float(team_data['fear_avg']),
                "surprise": float(team_data['surprise_avg']),
            },
            "message_count": team_data['total_messages'],
        }

        # User aggregates (anonymized, exclude user_hash)
        user_data = WellbeingAggregate.objects.filter(
            user_hash__isnull=False,
            source='overall',
            period_start__gte=start_date,
            period_end__lte=end_date
        ).exclude(user_hash=user.hashed_id).values('period_start', 'period_end').annotate(
            sentiment_avg=Avg('sentiment_weighted_avg'),
            stress_avg=Avg('stress_weighted_avg'),
            sadness_avg=Avg('emotion_sadness_avg'),
            joy_avg=Avg('emotion_joy_avg'),
            love_avg=Avg('emotion_love_avg'),
            anger_avg=Avg('emotion_anger_avg'),
            fear_avg=Avg('emotion_fear_avg'),
            surprise_avg=Avg('emotion_surprise_avg'),
            total_messages=Sum('message_count')
        ).order_by('-period_start')

        user_results = [
            {
                "period_start": agg['period_start'],
                "period_end": agg['period_end'],
                "sentiment_weighted_avg": float(agg['sentiment_avg'] or 0.0),
                "stress_weighted_avg": float(agg['stress_avg'] or 0.0),
                "emotions": {
                    "sadness": float(agg['sadness_avg'] or 0.0),
                    "joy": float(agg['joy_avg'] or 0.0),
                    "love": float(agg['love_avg'] or 0.0),
                    "anger": float(agg['anger_avg'] or 0.0),
                    "fear": float(agg['fear_avg'] or 0.0),
                    "surprise": float(agg['surprise_avg'] or 0.0),
                },
                "message_count": agg['total_messages'] or 0,
            } for agg in user_data
        ]

        # Channel aggregates
        channel_data = WellbeingAggregate.objects.filter(
            user_hash__isnull=False,
            source__in=['jira', 'chat', 'meeting'],
            period_start__gte=start_date,
            period_end__lte=end_date
        ).exclude(user_hash=user.hashed_id).values('source', 'period_start', 'period_end').annotate(
            sentiment_avg=Avg('sentiment_weighted_avg'),
            stress_avg=Avg('stress_weighted_avg'),
            sadness_avg=Avg('emotion_sadness_avg'),
            joy_avg=Avg('emotion_joy_avg'),
            love_avg=Avg('emotion_love_avg'),
            anger_avg=Avg('emotion_anger_avg'),
            fear_avg=Avg('emotion_fear_avg'),
            surprise_avg=Avg('emotion_surprise_avg'),
            total_messages=Sum('message_count')
        ).order_by('source', '-period_start')

        channel_results = [
            {
                "source": agg['source'],
                "period_start": agg['period_start'],
                "period_end": agg['period_end'],
                "sentiment_weighted_avg": float(agg['sentiment_avg'] or 0.0),
                "stress_weighted_avg": float(agg['stress_avg'] or 0.0),
                "emotions": {
                    "sadness": float(agg['sadness_avg'] or 0.0),
                    "joy": float(agg['joy_avg'] or 0.0),
                    "love": float(agg['love_avg'] or 0.0),
                    "anger": float(agg['anger_avg'] or 0.0),
                    "fear": float(agg['fear_avg'] or 0.0),
                    "surprise": float(agg['surprise_avg'] or 0.0),
                },
                "message_count": agg['total_messages'] or 0,
            } for agg in channel_data
        ]

        return {
            "team_aggregates": team_results,
            "user_aggregates": user_results,
            "channel_aggregates": channel_results,
            "calculated_at": timezone.now(),
        }
    except Exception as e:
        logger.error(f"Team well-being retrieval failed: {e}")
        raise MindPulseException(f"Failed to retrieve team well-being data: {str(e)}")