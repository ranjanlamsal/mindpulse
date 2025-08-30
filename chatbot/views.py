from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ChatbotSessionSerializer, ChatbotMessageSerializer
from .services import create_session, add_message
from .models import ChatbotSession


class ChatbotSessionView(APIView):
    def post(self, request):
        user_hash = request.data.get("user_hash")
        if not user_hash:
            return Response({"error": "user_hash required"}, status=status.HTTP_400_BAD_REQUEST)
        
        session = create_session(user_hash)
        return Response(ChatbotSessionSerializer(session).data, status=status.HTTP_201_CREATED)


class ChatbotMessageView(APIView):
    def post(self, request):
        serializer = ChatbotMessageSerializer(data=request.data)
        if serializer.is_valid():
            session_id = serializer.validated_data["session"].session_id
            msg = add_message(
                serializer.validated_data["session"],
                serializer.validated_data["sender"],
                serializer.validated_data["message"],
            )
            # TODO: integrate AI later for bot reply
            return Response(ChatbotMessageSerializer(msg).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
