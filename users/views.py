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

    def list(self, _):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        return Response(serializer.data)
    
    def retrieve(self, _, pk=None):
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user)

        return Response(serializer.data)
    
    def update(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user, data=request.data, partial=False)

        if serializer.is_valid():
            user = serializer.save()

            return Response(UserSerializer(user).data)
        
        return Response(serializer.errors, status=400)

    def partial_update(self, request, pk=None):
        user = get_object_or_404(User, id=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            user = serializer.save()

            return Response(UserSerializer(user).data)

        return Response(serializer.errors, status=400)

    def destroy(self, _, pk=None):
        user = get_object_or_404(User, id=pk)
        user.delete()

        return Response(status=204)
    