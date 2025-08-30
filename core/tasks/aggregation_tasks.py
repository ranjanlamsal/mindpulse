from celery import shared_task
from core.models.message_model import Message, MessageAnalysis
from core.models.user_model import User
from core.models.channel_model import Channel
from core.models.channel_model import WellbeingAggregate
from django.db import models
from django.db.models import Avg, Count, Sum
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

@shared_task
def aggregate_wellbeing():
    try:
        # Define daily time range
        now = timezone.now()
        period_start = now - timedelta(days=1)
        period_end = now

        users = User.objects.filter(is_active=True)
        channels = Channel.objects.filter(is_active=True)

        # Team-level aggregation (across all users)
        team_analyses = MessageAnalysis.objects.filter(
            message__created_at__range=(period_start, period_end)
        ).aggregate(
            sentiment_sum=Sum('sentiment_score', filter=models.Q(sentiment='positive')) or 0.0,
            neg_sentiment_sum=Sum('sentiment_score', filter=models.Q(sentiment='negative')) or 0.0,
            stress_sum=Sum('stress_score', filter=models.Q(stress=True)) or 0.0,
            no_stress_sum=Sum('stress_score', filter=models.Q(stress=False)) or 0.0,
            sadness_sum=Sum('emotion_score', filter=models.Q(emotion='sadness')) or 0.0,
            joy_sum=Sum('emotion_score', filter=models.Q(emotion='joy')) or 0.0,
            love_sum=Sum('emotion_score', filter=models.Q(emotion='love')) or 0.0,
            anger_sum=Sum('emotion_score', filter=models.Q(emotion='anger')) or 0.0,
            fear_sum=Sum('emotion_score', filter=models.Q(emotion='fear')) or 0.0,
            surprise_sum=Sum('emotion_score', filter=models.Q(emotion='surprise')) or 0.0,
            sadness_count=Count('id', filter=models.Q(emotion='sadness')),
            joy_count=Count('id', filter=models.Q(emotion='joy')),
            love_count=Count('id', filter=models.Q(emotion='love')),
            anger_count=Count('id', filter=models.Q(emotion='anger')),
            fear_count=Count('id', filter=models.Q(emotion='fear')),
            surprise_count=Count('id', filter=models.Q(emotion='surprise')),
            total_count=Count('id')
        )

        if team_analyses['total_count'] > 0:
            sentiment_weighted_avg = (
                (team_analyses['sentiment_sum'] - team_analyses['neg_sentiment_sum'])
                / team_analyses['total_count']
            )
            stress_weighted_avg = (
                (team_analyses['stress_sum'] - team_analyses['no_stress_sum'])
                / team_analyses['total_count']
            )
            WellbeingAggregate.objects.update_or_create(
                user_hash=None,  # Team-level
                source='overall',
                period_start=period_start,
                defaults={
                    'period_end': period_end,
                    'sentiment_weighted_avg': sentiment_weighted_avg,
                    'stress_weighted_avg': stress_weighted_avg,
                    'emotion_sadness_avg': team_analyses['sadness_sum'] / team_analyses['sadness_count'] if team_analyses['sadness_count'] > 0 else 0.0,
                    'emotion_joy_avg': team_analyses['joy_sum'] / team_analyses['joy_count'] if team_analyses['joy_count'] > 0 else 0.0,
                    'emotion_love_avg': team_analyses['love_sum'] / team_analyses['love_count'] if team_analyses['love_count'] > 0 else 0.0,
                    'emotion_anger_avg': team_analyses['anger_sum'] / team_analyses['anger_count'] if team_analyses['anger_count'] > 0 else 0.0,
                    'emotion_fear_avg': team_analyses['fear_sum'] / team_analyses['fear_count'] if team_analyses['fear_count'] > 0 else 0.0,
                    'emotion_surprise_avg': team_analyses['surprise_sum'] / team_analyses['surprise_count'] if team_analyses['surprise_count'] > 0 else 0.0,
                    'message_count': team_analyses['total_count'],
                }
            )

        # User and channel-level aggregation
        for user in users:
            # Overall user aggregation
            user_analyses = MessageAnalysis.objects.filter(
                message__user_hash=user.hashed_id,
                message__created_at__range=(period_start, period_end)
            ).aggregate(
                sentiment_sum=Sum('sentiment_score', filter=models.Q(sentiment='positive')) or 0.0,
                neg_sentiment_sum=Sum('sentiment_score', filter=models.Q(sentiment='negative')) or 0.0,
                stress_sum=Sum('stress_score', filter=models.Q(stress=True)) or 0.0,
                no_stress_sum=Sum('stress_score', filter=models.Q(stress=False)) or 0.0,
                sadness_sum=Sum('emotion_score', filter=models.Q(emotion='sadness')) or 0.0,
                joy_sum=Sum('emotion_score', filter=models.Q(emotion='joy')) or 0.0,
                love_sum=Sum('emotion_score', filter=models.Q(emotion='love')) or 0.0,
                anger_sum=Sum('emotion_score', filter=models.Q(emotion='anger')) or 0.0,
                fear_sum=Sum('emotion_score', filter=models.Q(emotion='fear')) or 0.0,
                surprise_sum=Sum('emotion_score', filter=models.Q(emotion='surprise')) or 0.0,
                sadness_count=Count('id', filter=models.Q(emotion='sadness')),
                joy_count=Count('id', filter=models.Q(emotion='joy')),
                love_count=Count('id', filter=models.Q(emotion='love')),
                anger_count=Count('id', filter=models.Q(emotion='anger')),
                fear_count=Count('id', filter=models.Q(emotion='fear')),
                surprise_count=Count('id', filter=models.Q(emotion='surprise')),
                total_count=Count('id')
            )

            if user_analyses['total_count'] > 0:
                sentiment_weighted_avg = (
                    (user_analyses['sentiment_sum'] - user_analyses['neg_sentiment_sum'])
                    / user_analyses['total_count']
                )
                stress_weighted_avg = (
                    (user_analyses['stress_sum'] - user_analyses['no_stress_sum'])
                    / user_analyses['total_count']
                )
                WellbeingAggregate.objects.update_or_create(
                    user_hash=user.hashed_id,
                    source='overall',
                    period_start=period_start,
                    defaults={
                        'period_end': period_end,
                        'sentiment_weighted_avg': sentiment_weighted_avg,
                        'stress_weighted_avg': stress_weighted_avg,
                        'emotion_sadness_avg': user_analyses['sadness_sum'] / user_analyses['sadness_count'] if user_analyses['sadness_count'] > 0 else 0.0,
                        'emotion_joy_avg': user_analyses['joy_sum'] / user_analyses['joy_count'] if user_analyses['joy_count'] > 0 else 0.0,
                        'emotion_love_avg': user_analyses['love_sum'] / user_analyses['love_count'] if user_analyses['love_count'] > 0 else 0.0,
                        'emotion_anger_avg': user_analyses['anger_sum'] / user_analyses['anger_count'] if user_analyses['anger_count'] > 0 else 0.0,
                        'emotion_fear_avg': user_analyses['fear_sum'] / user_analyses['fear_count'] if user_analyses['fear_count'] > 0 else 0.0,
                        'emotion_surprise_avg': user_analyses['surprise_sum'] / user_analyses['surprise_count'] if user_analyses['surprise_count'] > 0 else 0.0,
                        'message_count': user_analyses['total_count'],
                    }
                )

            # Channel-level aggregation for each user
            for channel in channels:
                channel_analyses = MessageAnalysis.objects.filter(
                    message__user_hash=user.hashed_id,
                    message__channel=channel,
                    message__created_at__range=(period_start, period_end)
                ).aggregate(
                    sentiment_sum=Sum('sentiment_score', filter=models.Q(sentiment='positive')) or 0.0,
                    neg_sentiment_sum=Sum('sentiment_score', filter=models.Q(sentiment='negative')) or 0.0,
                    stress_sum=Sum('stress_score', filter=models.Q(stress=True)) or 0.0,
                    no_stress_sum=Sum('stress_score', filter=models.Q(stress=False)) or 0.0,
                    sadness_sum=Sum('emotion_score', filter=models.Q(emotion='sadness')) or 0.0,
                    joy_sum=Sum('emotion_score', filter=models.Q(emotion='joy')) or 0.0,
                    love_sum=Sum('emotion_score', filter=models.Q(emotion='love')) or 0.0,
                    anger_sum=Sum('emotion_score', filter=models.Q(emotion='anger')) or 0.0,
                    fear_sum=Sum('emotion_score', filter=models.Q(emotion='fear')) or 0.0,
                    surprise_sum=Sum('emotion_score', filter=models.Q(emotion='surprise')) or 0.0,
                    sadness_count=Count('id', filter=models.Q(emotion='sadness')),
                    joy_count=Count('id', filter=models.Q(emotion='joy')),
                    love_count=Count('id', filter=models.Q(emotion='love')),
                    anger_count=Count('id', filter=models.Q(emotion='anger')),
                    fear_count=Count('id', filter=models.Q(emotion='fear')),
                    surprise_count=Count('id', filter=models.Q(emotion='surprise')),
                    total_count=Count('id')
                )

                if channel_analyses['total_count'] > 0:
                    sentiment_weighted_avg = (
                        (channel_analyses['sentiment_sum'] - channel_analyses['neg_sentiment_sum'])
                        / channel_analyses['total_count']
                    )
                    stress_weighted_avg = (
                        (channel_analyses['stress_sum'] - channel_analyses['no_stress_sum'])
                        / channel_analyses['total_count']
                    )
                    WellbeingAggregate.objects.update_or_create(
                        user_hash=user.hashed_id,
                        source=channel.type,
                        period_start=period_start,
                        defaults={
                            'period_end': period_end,
                            'sentiment_weighted_avg': sentiment_weighted_avg,
                            'stress_weighted_avg': stress_weighted_avg,
                            'emotion_sadness_avg': channel_analyses['sadness_sum'] / channel_analyses['sadness_count'] if channel_analyses['sadness_count'] > 0 else 0.0,
                            'emotion_joy_avg': channel_analyses['joy_sum'] / channel_analyses['joy_count'] if channel_analyses['joy_count'] > 0 else 0.0,
                            'emotion_love_avg': channel_analyses['love_sum'] / channel_analyses['love_count'] if channel_analyses['love_count'] > 0 else 0.0,
                            'emotion_anger_avg': channel_analyses['anger_sum'] / channel_analyses['anger_count'] if channel_analyses['anger_count'] > 0 else 0.0,
                            'emotion_fear_avg': channel_analyses['fear_sum'] / channel_analyses['fear_count'] if channel_analyses['fear_count'] > 0 else 0.0,
                            'emotion_surprise_avg': channel_analyses['surprise_sum'] / channel_analyses['surprise_count'] if channel_analyses['surprise_count'] > 0 else 0.0,
                            'message_count': channel_analyses['total_count'],
                        }
                    )

    except Exception as e:
        logger.error(f"Error in wellbeing aggregation: {e}")
