# from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404

from rest_framework import views, viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import Token

from .models import User
from .permissions import (
    CanCreateUser,
    CanDeleteUser,
    CanListUsers,
    CanPartialUpdateUser,
    CanRetrieveUser,
    CanUpdateUser,
)
from .serializers import UserCreationSerializer, UserLoginSerializer, UserSerializer

class UserLoginView(views.APIView):
    permission_classes = []
    serializer_class = UserLoginSerializer

    def post(self: views, request: views.Request) -> Response: 
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid() or True: 
            user = authenticate(
                username = serializer.validated_data["username"],
                password = serializer.validated_data["password"],
            )

            if user: 
                token, _ = Token.objects.get_or_create(user=user)
                return Response({"token": token.key})
            else: 
                return Response({"error": 'Invalid credentials'}, status=401)
        return Response(serializer.errors, status=400)

class UserViewSet(viewsets.ViewSet): 
    permission_classes = []
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action == "create":
            self.permission_classes = [CanCreateUser]
        elif self.action == 'list':
            self.permission_classes = [CanListUsers]
        elif self.action == 'retrieve':
            self.permission_classes = [CanRetrieveUser]
        elif self.action == 'update':
                    self.permission_classes = [CanUpdateUser]
        elif self.action == 'partial_update':
                    self.permission_classes = [CanPartialUpdateUser]
        elif self.action == 'destroy':
                    self.permission_classes = [CanDeleteUser]

        return [permission() for permission in self.permission_classes]
    