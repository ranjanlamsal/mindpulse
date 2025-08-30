"""
Chatbot serializers for emotional support functionality.
"""
from rest_framework import serializers
from chatbot.models import Conversation, Message


class ChatMessageSerializer(serializers.Serializer):
    """
    Serializer for chatbot message input.
    """
    message = serializers.CharField(max_length=5000, allow_blank=False)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_message(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Message cannot be empty.")
        return value.strip()


class ConversationSerializer(serializers.ModelSerializer):
    """
    Serializer for conversation data.
    """
    last_message_preview = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'status', 'created_at', 'updated_at',
            'favourite', 'archive', 'follow_up_needed', 'crisis_flags',
            'last_message_preview'
        ]

    def get_last_message_preview(self, obj):
        """Get preview of the last message."""
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            preview = last_message.content[:100]
            return preview + "..." if len(last_message.content) > 100 else preview
        return "No messages yet"


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for message data.
    """
    class Meta:
        model = Message
        fields = [
            'id', 'content', 'is_from_user', 'emotions', 
            'crisis_level', 'support_request', 'created_at'
        ]