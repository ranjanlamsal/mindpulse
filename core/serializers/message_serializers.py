from rest_framework.serializers import (
    Serializer, CharField, UUIDField, DateTimeField
)
from rest_framework import serializers
from core.models.user_model import User

class MessageIngestionSerializer(Serializer):
    channel_id = CharField(max_length=100)
    external_ref = CharField(max_length=255, required=False)
    username = CharField(max_length=150)
    message = CharField()

    def validate(self, attrs):
        """
        Transform username to user_hash using the User model function.
        """
        try:
            attrs['user_hash'] = User.get_hashed_id_by_username(attrs.pop('username'))
        except User.DoesNotExist:
            raise serializers.ValidationError(f"User with username '{attrs['username']}' not found.")
        return attrs
