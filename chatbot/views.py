"""
Chatbot views for emotional support functionality.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes

from chatbot.services import EmotionalSupportChatbotService
from chatbot.serializers import ChatMessageSerializer, ConversationSerializer
from core.utils.response_builder import APIResponseBuilder
import logging

logger = logging.getLogger(__name__)


class ChatView(APIView):
    """
    Main chat endpoint for emotional support chatbot.
    Open access for external servers.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """Send message to chatbot and get response."""
        try:
            serializer = ChatMessageSerializer(data=request.data)
            if not serializer.is_valid():
                return APIResponseBuilder.error(
                    message="Invalid message data",
                    errors=serializer.errors,
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # For unauthenticated access, pass None as user
            user = getattr(request, 'user', None) if hasattr(request, 'user') and request.user.is_authenticated else None
            chatbot_service = EmotionalSupportChatbotService(user)
            response_data = chatbot_service.process_user_message(
                conversation_id=serializer.validated_data.get('conversation_id'),
                message_content=serializer.validated_data['message']
            )

            if 'error' in response_data:
                return APIResponseBuilder.error(
                    message=response_data['error'],
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return APIResponseBuilder.success(
                data=response_data,
                message="Message processed successfully"
            )

        except Exception as e:
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'
            logger.error(f"Chat error for user {user_id}: {str(e)}")
            return APIResponseBuilder.error(
                message="Unable to process your message right now",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationListView(APIView):
    """
    List all conversations for the user.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        """Get all conversations for the user."""
        try:
            user = getattr(request, 'user', None) if hasattr(request, 'user') and request.user.is_authenticated else None
            chatbot_service = EmotionalSupportChatbotService(user)
            conversations = chatbot_service.list_conversations()

            return APIResponseBuilder.success(
                data=conversations,
                message="Conversations retrieved successfully"
            )

        except Exception as e:
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'
            logger.error(f"Error retrieving conversations for user {user_id}: {str(e)}")
            return APIResponseBuilder.error(
                message="Unable to retrieve conversations",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ConversationHistoryView(APIView):
    """
    Get conversation history for a specific conversation.
    """
    permission_classes = [AllowAny]

    def get(self, request, conversation_id):
        """Get message history for a conversation."""
        try:
            limit = request.query_params.get('limit', 50)
            try:
                limit = int(limit)
            except ValueError:
                limit = 50

            user = getattr(request, 'user', None) if hasattr(request, 'user') and request.user.is_authenticated else None
            chatbot_service = EmotionalSupportChatbotService(user)
            messages = chatbot_service.get_conversation_history(conversation_id, limit)

            return APIResponseBuilder.success(
                data=messages,
                message="Conversation history retrieved successfully"
            )

        except Exception as e:
            user_id = request.user.id if hasattr(request, 'user') and request.user.is_authenticated else 'anonymous'
            logger.error(f"Error retrieving conversation {conversation_id} for user {user_id}: {str(e)}")
            return APIResponseBuilder.error(
                message="Unable to retrieve conversation history",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )