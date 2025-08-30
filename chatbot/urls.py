"""
Chatbot URL patterns for emotional support functionality.
"""
from django.urls import path
from chatbot.views import ChatView, ConversationListView, ConversationHistoryView

urlpatterns = [
    # Main chat endpoint
    path('chat/', ChatView.as_view(), name='chatbot_chat'),
    
    # Conversation management
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/<int:conversation_id>/messages/', ConversationHistoryView.as_view(), name='conversation_history'),
]