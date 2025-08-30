"""
Analytics views with proper error handling and response building.
Refactored for maintainability and performance.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from core.permissions import IsManagerOrAdmin
from core.services.analytics_service import get_team_analytics, AnalyticsService
from core.services.user_service import UserService
from core.models.user_model import User
from core.models.channel_model import WellbeingAggregate
from core.models.message_model import MessageAnalysis, Message
from core.exceptions import (
    AuthorizationError, 
    MindPulseException, 
    ValidationError,
    InvalidUserError
)
from core.utils.response_builder import APIResponseBuilder, success_response
from core.utils.validators import DateValidator, UUIDValidator, ValidationError as ValidatorError
from core.utils.logging_config import PerformanceLogger
from django.db.models import Avg, Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from dateutil.parser import isoparse
import logging

logger = logging.getLogger(__name__)

class TeamDashboardView(APIView):
    """
    Comprehensive team analytics for management dashboard.
    GET /analytics/team-dashboard/
    """
    permission_classes = [IsManagerOrAdmin]
    
    def get(self, request):
        """Get team dashboard analytics with proper error handling."""
        with PerformanceLogger("team_dashboard_analytics", logger):
            try:
                # Parse and validate date parameters
                start_date, end_date = DateValidator.parse_date_range(
                    request.query_params.get('start_date'),
                    request.query_params.get('end_date'),
                    default_days=30
                )
                
                # Get comprehensive analytics
                data = get_team_analytics(start_date, end_date)
                
                return APIResponseBuilder.success(
                    data=data,
                    message="Team analytics retrieved successfully"
                )
                
            except ValidatorError as e:
                return APIResponseBuilder.validation_error(e.message)
            except MindPulseException as e:
                return APIResponseBuilder.error(e.message, e.status_code)
            except Exception as e:
                logger.error(f"Unexpected error in team dashboard: {str(e)}")
                return APIResponseBuilder.internal_error(
                    "Failed to retrieve team analytics",
                    str(e)
                )

class UserWellbeingView(APIView):
    """
    Individual user wellbeing data (employees can see their own data)
    GET /analytics/user-wellbeing/?user_hash=<uuid>
    """
    
    def get(self, request):
        try:
            user_hash = request.query_params.get('user_hash')
            if not user_hash:
                return Response({
                    "error": "user_hash parameter is required"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Parse date parameters
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)
            
            if start_date_str and end_date_str:
                try:
                    start_date = isoparse(start_date_str).replace(tzinfo=timezone.utc)
                    end_date = isoparse(end_date_str).replace(tzinfo=timezone.utc)
                except ValueError:
                    return Response({
                        "error": "Invalid date format. Use ISO 8601"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user's wellbeing data
            user_data = WellbeingAggregate.objects.filter(
                user_hash=user_hash,
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
            
            # Get daily breakdown
            daily_data = WellbeingAggregate.objects.filter(
                user_hash=user_hash,
                source='overall',
                period_start__gte=start_date,
                period_end__lte=end_date
            ).values('period_start', 'period_end').annotate(
                sentiment=Avg('sentiment_weighted_avg'),
                stress=Avg('stress_weighted_avg'),
                joy=Avg('emotion_joy_avg'),
                sadness=Avg('emotion_sadness_avg'),
                anger=Avg('emotion_anger_avg'),
                fear=Avg('emotion_fear_avg'),
                love=Avg('emotion_love_avg'),
                surprise=Avg('emotion_surprise_avg'),
                messages=Sum('message_count')
            ).order_by('period_start')
            
            # Get channel breakdown
            channel_data = WellbeingAggregate.objects.filter(
                user_hash=user_hash,
                source__in=['discord', 'meeting', 'jira', 'chat'],
                period_start__gte=start_date,
                period_end__lte=end_date
            ).values('source').annotate(
                sentiment=Avg('sentiment_weighted_avg'),
                stress=Avg('stress_weighted_avg'),
                joy=Avg('emotion_joy_avg'),
                sadness=Avg('emotion_sadness_avg'),
                anger=Avg('emotion_anger_avg'),
                fear=Avg('emotion_fear_avg'),
                love=Avg('emotion_love_avg'),
                surprise=Avg('emotion_surprise_avg'),
                messages=Sum('message_count')
            )
            
            from core.services.analytics_service import calculate_wellbeing_score, format_emotions_data
            
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
            
            response_data = {
                "user_hash": user_hash,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "calculated_at": timezone.now().isoformat()
                },
                "overall_metrics": {
                    "sentiment_weighted_avg": float(user_data['sentiment_avg']),
                    "stress_weighted_avg": float(user_data['stress_avg']),
                    "emotions": emotions,
                    "message_count": user_data['total_messages'],
                    "wellbeing_score": wellbeing_score
                },
                "daily_trends": [
                    {
                        "date": item['period_start'].isoformat(),
                        "sentiment": float(item['sentiment'] or 0),
                        "stress": float(item['stress'] or 0),
                        "emotions": format_emotions_data({
                            'joy': item['joy'],
                            'sadness': item['sadness'],
                            'anger': item['anger'],
                            'fear': item['fear'],
                            'love': item['love'],
                            'surprise': item['surprise']
                        }),
                        "message_count": item['messages'] or 0,
                        "wellbeing_score": calculate_wellbeing_score(
                            item['sentiment'] or 0,
                            item['stress'] or 0,
                            format_emotions_data({
                                'joy': item['joy'],
                                'sadness': item['sadness'],
                                'anger': item['anger'],
                                'fear': item['fear'],
                                'love': item['love'],
                                'surprise': item['surprise']
                            })
                        )
                    } for item in daily_data
                ],
                "channel_breakdown": [
                    {
                        "source": item['source'],
                        "sentiment": float(item['sentiment'] or 0),
                        "stress": float(item['stress'] or 0),
                        "emotions": format_emotions_data({
                            'joy': item['joy'],
                            'sadness': item['sadness'],
                            'anger': item['anger'],
                            'fear': item['fear'],
                            'love': item['love'],
                            'surprise': item['surprise']
                        }),
                        "message_count": item['messages'] or 0,
                        "wellbeing_score": calculate_wellbeing_score(
                            item['sentiment'] or 0,
                            item['stress'] or 0,
                            format_emotions_data({
                                'joy': item['joy'],
                                'sadness': item['sadness'],
                                'anger': item['anger'],
                                'fear': item['fear'],
                                'love': item['love'],
                                'surprise': item['surprise']
                            })
                        )
                    } for item in channel_data
                ]
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"User wellbeing error: {e}")
            return Response({
                "error": f"Failed to retrieve user wellbeing data: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ChannelComparisonView(APIView):
    """
    Compare wellbeing across different channels
    GET /analytics/channel-comparison/
    """
    
    def get(self, request):
        try:
            # Parse date parameters
            start_date_str = request.query_params.get('start_date')
            end_date_str = request.query_params.get('end_date')
            
            end_date = timezone.now()
            start_date = end_date - timedelta(days=7)  # Default to last week
            
            if start_date_str and end_date_str:
                try:
                    start_date = isoparse(start_date_str).replace(tzinfo=timezone.utc)
                    end_date = isoparse(end_date_str).replace(tzinfo=timezone.utc)
                except ValueError:
                    return Response({
                        "error": "Invalid date format"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get channel comparison data
            channel_stats = WellbeingAggregate.objects.filter(
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
                active_users=Count('user_hash', distinct=True),
                avg_messages_per_user=Avg('message_count')
            ).order_by('-total_messages')
            
            from core.services.analytics_service import calculate_wellbeing_score, format_emotions_data, get_alert_level
            
            channels_data = []
            for channel in channel_stats:
                emotions = format_emotions_data({
                    'joy': channel['joy_avg'],
                    'sadness': channel['sadness_avg'],
                    'anger': channel['anger_avg'],
                    'fear': channel['fear_avg'],
                    'love': channel['love_avg'],
                    'surprise': channel['surprise_avg']
                })
                
                wellbeing_score = calculate_wellbeing_score(
                    channel['sentiment_avg'],
                    channel['stress_avg'],
                    emotions
                )
                
                channels_data.append({
                    "source": channel['source'],
                    "sentiment_weighted_avg": float(channel['sentiment_avg'] or 0),
                    "stress_weighted_avg": float(channel['stress_avg'] or 0),
                    "emotions": emotions,
                    "total_messages": channel['total_messages'] or 0,
                    "active_users": channel['active_users'],
                    "avg_messages_per_user": float(channel['avg_messages_per_user'] or 0),
                    "wellbeing_score": wellbeing_score,
                    "alert_level": get_alert_level(wellbeing_score, channel['stress_avg'] or 0)
                })
            
            response_data = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "calculated_at": timezone.now().isoformat()
                },
                "channels": channels_data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Channel comparison error: {e}")
            return Response({
                "error": f"Failed to retrieve channel comparison: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class AlertsView(APIView):
    """
    Get current alerts and notifications
    GET /analytics/alerts/
    """
    
    def get(self, request):
        try:
            # Get recent data for alert generation
            end_date = timezone.now()
            start_date = end_date - timedelta(days=7)
            
            # Get team analytics which includes alerts
            analytics_data = get_team_analytics(start_date, end_date)
            
            # Add some additional alert logic
            alerts = analytics_data.get("alerts", [])
            
            # Check for trending issues
            recent_data = WellbeingAggregate.objects.filter(
                period_start__gte=start_date,
                period_end__lte=end_date
            )
            
            total_users = recent_data.filter(user_hash__isnull=False, source='overall').values('user_hash').distinct().count()
            
            if total_users > 0:
                # Check engagement levels
                low_engagement_users = recent_data.filter(
                    user_hash__isnull=False,
                    source='overall',
                    message_count__lt=5
                ).values('user_hash').distinct().count()
                
                if low_engagement_users > total_users * 0.3:  # More than 30% low engagement
                    alerts.append({
                        "type": "low_engagement",
                        "severity": "medium",
                        "message": f"{low_engagement_users} employees showing low communication engagement",
                        "count": low_engagement_users,
                        "action_required": False
                    })
            
            response_data = {
                "timestamp": timezone.now().isoformat(),
                "alerts": alerts,
                "summary": {
                    "total_alerts": len(alerts),
                    "high_severity": len([a for a in alerts if a.get("severity") == "high"]),
                    "medium_severity": len([a for a in alerts if a.get("severity") == "medium"]),
                    "requires_action": len([a for a in alerts if a.get("action_required")])
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Alerts error: {e}")
            return Response({
                "error": f"Failed to retrieve alerts: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class WellbeingTrendsView(APIView):
    """
    Get wellbeing trends over time
    GET /analytics/trends/?period=week|month|quarter
    """
    
    def get(self, request):
        try:
            period = request.query_params.get('period', 'month')
            
            end_date = timezone.now()
            if period == 'week':
                start_date = end_date - timedelta(days=7)
                interval = 'day'
            elif period == 'month':
                start_date = end_date - timedelta(days=30)
                interval = 'day'
            elif period == 'quarter':
                start_date = end_date - timedelta(days=90)
                interval = 'week'
            else:
                return Response({
                    "error": "Invalid period. Use 'week', 'month', or 'quarter'"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get trend data
            trend_data = WellbeingAggregate.objects.filter(
                user_hash__isnull=True,  # Team level data
                source='overall',
                period_start__gte=start_date,
                period_end__lte=end_date
            ).values('period_start', 'period_end').annotate(
                sentiment_avg=Avg('sentiment_weighted_avg'),
                stress_avg=Avg('stress_weighted_avg'),
                joy_avg=Avg('emotion_joy_avg'),
                sadness_avg=Avg('emotion_sadness_avg'),
                anger_avg=Avg('emotion_anger_avg'),
                fear_avg=Avg('emotion_fear_avg'),
                love_avg=Avg('emotion_love_avg'),
                surprise_avg=Avg('emotion_surprise_avg'),
                message_count=Sum('message_count')
            ).order_by('period_start')
            
            from core.services.analytics_service import calculate_wellbeing_score, format_emotions_data
            
            trends = []
            for item in trend_data:
                emotions = format_emotions_data({
                    'joy': item['joy_avg'],
                    'sadness': item['sadness_avg'],
                    'anger': item['anger_avg'],
                    'fear': item['fear_avg'],
                    'love': item['love_avg'],
                    'surprise': item['surprise_avg']
                })
                
                wellbeing_score = calculate_wellbeing_score(
                    item['sentiment_avg'],
                    item['stress_avg'],
                    emotions
                )
                
                trends.append({
                    "date": item['period_start'].isoformat(),
                    "sentiment": float(item['sentiment_avg'] or 0),
                    "stress": float(item['stress_avg'] or 0),
                    "emotions": emotions,
                    "message_count": item['message_count'] or 0,
                    "wellbeing_score": wellbeing_score
                })
            
            response_data = {
                "period": period,
                "interval": interval,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "trends": trends
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Trends error: {e}")
            return Response({
                "error": f"Failed to retrieve trends: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)