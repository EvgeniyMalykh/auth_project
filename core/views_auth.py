import bcrypt
from rest_framework import status, views
from rest_framework.response import Response

from .models import User
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
from .permissions import IsAuthenticatedCustom
from .utils import generate_jwt


class RegisterView(views.APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(
            UserProfileSerializer(user).data, status=status.HTTP_201_CREATED
        )


class LoginView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not user.is_active:
            return Response(
                {"detail": "User is inactive"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not bcrypt.checkpw(
            password.encode("utf-8"), user.password_hash.encode("utf-8")
        ):
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        token = generate_jwt(user.id)
        return Response({"access_token": token})


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticatedCustom]

    def post(self, request):
        return Response(status=status.HTTP_204_NO_CONTENT)
