from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.serializers.channel_serializers import ChannelCreateSerializer
from core.services.channel_services import get_or_create_channel
from core.models.channel_model import Channel


class ChannelListCreateView(APIView):
    authentication_classes = []
    permission_classes = []
    def post(self, request):
        try:
            serializer = ChannelCreateSerializer(data = request.data)

            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            data = serializer.validated_data
            channel, created = get_or_create_channel(data)

            message = "Channel Created Successfully" if created else "Channel Retrieved Successfully"

            return Response(
                {
                    "message":message,
                    "data": {
                        "id": channel.id,
                        "name":channel.name,
                        "external_id": channel.external_id,
                        "type": channel.type
                    }
                },
                status = status.HTTP_201_CREATED if created else status.HTTP_200_OK
                
            )
        
        except Exception as e:
            return Response(
                {
                    "error": f"Unexpected Error: {str(e)}"
                }
            )
        
