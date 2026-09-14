# from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.shortcuts import get_object_or_404

from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

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

    @extend_schema(
        request=UserLoginSerializer,
        responses={
             200: OpenApiTypes.OBJECT,
             400: "Bad request",
             401: "Invalid credentials were provided.",
             500: "Internal server error.",
        },
    )

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

    @extend_schema(
        request=UserCreationSerializer,
        responses={
            201: UserSerializer,
            400: "Bad request",
            401: "Authentication credentials were not provided",
            403: "You do not have permission to perform this action.",
            500: "Internal server error.",
        },
    )

    def create(self, request):
        user = User(**request.data)
        validate_password(request.data.get("password", ""),user=user)
        user.set_password(request.data.get("password", ""))
        serializer = UserSerializer(user, data=request.data)

        if serializer.is_valid():
            if user.role == User.ADMIN:
                user.is_staff = True
                user.is_superuser = True
                user.save()

                group = Group.objects.get(name="admin")
                group.user_set.add(user)

            elif user.role == User.MODERATOR:
                user.is_staff = True
                user.is_superuser = False
                user.save()

                group = Group.objects.get(name="moderator")
                group.user_set.add(user)

            else: #User role is USER
                user.is_staff = False
                user.is_superuser = False
                user.save()

                group = Group.objects.get(name="user")
                group.user_set.add(user)

            return Response(serializer.data, status=201)
        
        return Response(serializer.errors, status=400)

    @extend_schema(
        responses= {
            200: UserSerializer,
            400: "Bad request",
            401: "Authentication credentials were not provided",
            500: "Internal server error",
        },
    )

    def list(self, _):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)

    @extend_schema(
        responses={
            200: UserSerializer,
            400: "Bad request",
            401: "Authentication credentials were not provided",
            404: "User not found",
            500: "Internal server error",
        },
    )
    
    def retrieve(self, _, pk=None):
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user)

        return Response(serializer.data)

    @extend_schema(
        responses={
            200: UserSerializer,
            400: "Bad request",
            401: "Authentication credentials were not provided",
            403: "You don't have permission to perform this action",
            500: "Internal server error",
        },
    )
    
    def update(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user, data=request.data, partial=False)

        if serializer.is_valid():
            user = serializer.save()

            return Response(UserSerializer(user).data)
        
        return Response(serializer.errors, status=400)

    @extend_schema(
        responses={
            200: UserSerializer,
            400: "Bad request",
            401: "Authentication credentials were not provided",
            403: "You don't have permission to perform this action",
            404: "User not found",
            500: "Internal server error",
        },
    )

    def partial_update(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            user = serializer.save()

            return Response(UserSerializer(user).data)

        return Response(serializer.errors, status=400)

    @extend_schema(
        responses={
            204: None,
            400: "Bad request",
            401: "Authentication credentials were not provided",
            403: "You don't have permission to perform this action",
            404: "User not found",
            500: "Internal server error",
        },
    )

    def destroy(self, _, pk=None):
        user = get_object_or_404(User, id=pk)
        user.delete()

        return Response(status=204)
    