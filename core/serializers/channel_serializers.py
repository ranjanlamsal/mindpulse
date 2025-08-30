from rest_framework.serializers import (
    ModelSerializer
)
from core.models.channel_model import Channel

class ChannelListSerializer(ModelSerializer):
    class Meta:
        model = Channel
        fields = ["id", "name", "external_id"]

class ChannelCreateSerializer(ModelSerializer):
    class Meta:
        model = Channel
        fields = ["name", "type", "external_id"]
        read_only_fields = ["id"]
        extra_kwargs = {
            "type": {"required": True},
            "name": {"required": True},
            "external_id": {"required": True}
        }
    