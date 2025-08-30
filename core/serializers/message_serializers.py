from rest_framework.serializers import (
    Serializer, CharField, UUIDField, DateTimeField
)


class MessageIngestionSerializer(Serializer):
    channel_id = CharField(max_length=100)
    external_ref = CharField(max_length=255, required=False)
    user_hash = UUIDField()
    message = CharField()
