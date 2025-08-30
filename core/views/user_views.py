from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.serializers.user_serializers import SignupSerializer, LoginSerializer
from core.services.user_services import signup_user, login_user


class SignupView(APIView):
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = signup_user(serializer.validated_data)
            return Response({"message": "User created successfully", "username": user.username})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = login_user(serializer.validated_data["username"], serializer.validated_data["password"])
            if not user:
                return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
            return Response({"message": "Login successful", "username": user.username, "role": user.role, "user_hash" : user.hashed_id})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
