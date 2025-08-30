from rest_framework import serializers
from .models import ChatbotSession, ChatbotMessage


class ChatbotSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotSession
        fields = ["session_id", "user_hash", "started_at"]


class ChatbotMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotMessage
        fields = ["id", "session", "user_message", "ai_message", "created_at"]
