from core.models.channel_model import Channel
from core.exceptions import (
    MindPulseException,
    InvalidChannelError
)


def get_or_create_channel(validated_data):
    try:
        channel, created = Channel.get_or_create_channel_instance(
            name = validated_data["name"],
            type = validated_data["type"],
            external_id = validated_data["external_id"]
        )

        return channel, created
    except Exception as e:
        raise MindPulseException(f"Failed to get or create channel: {str(e)}")
    