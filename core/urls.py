from django.urls import path, include
from core.views.user_views import SignupView, LoginView
from core.views.channel_views import ChannelListCreateView
from core.views.message_views import MessageView, TeamWellbeingView
from core.views.analytics_views import (
    TeamDashboardView,
    UserWellbeingView,
    ChannelComparisonView,
    AlertsView,
    WellbeingTrendsView
)

# Authentication & Core APIs (Legacy - kept for backward compatibility)
legacy_auth_patterns = [
    path("signup/", SignupView.as_view(), name="signup-legacy"),
    path("login/", LoginView.as_view(), name="login-legacy"),
]

# New JWT Authentication patterns
from core.urls.auth_urls import urlpatterns as auth_urlpatterns

# Data Ingestion APIs
data_patterns = [
    path("channels/", ChannelListCreateView.as_view(), name="channels"),
    path("messages/", MessageView.as_view(), name="messages"),
]

# Analytics & Dashboard APIs
analytics_patterns = [
    path("team-dashboard/", TeamDashboardView.as_view(), name="team-dashboard"),
    path("user-wellbeing/", UserWellbeingView.as_view(), name="user-wellbeing"),
    path("channel-comparison/", ChannelComparisonView.as_view(), name="channel-comparison"),
    path("alerts/", AlertsView.as_view(), name="alerts"),
    path("trends/", WellbeingTrendsView.as_view(), name="trends"),
    # Legacy endpoint for backward compatibility
    path("team-wellbeing/", TeamWellbeingView.as_view(), name="team-wellbeing-legacy"),
]

urlpatterns = [
    # New JWT Authentication
    path("auth/", include(auth_urlpatterns)),
    
    # Legacy Authentication (backward compatibility)
    *legacy_auth_patterns,
    
    # Data Ingestion
    *data_patterns,
    
    # Analytics
    path("analytics/", include(analytics_patterns)),
]
