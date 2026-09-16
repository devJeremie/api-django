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
    """Dead code: not registered in any urls.py (api/urls.py or users/urls.py).
    JWT login actually goes through simplejwt's TokenObtainPairView at
    /login. Left here from an earlier iteration; also depends on
    UserLoginSerializer, which has its own bug (see serializers.py), and on
    rest_framework_simplejwt.tokens.Token, which doesn't provide the
    Token.objects.get_or_create(...) API used below (that's the DRF
    authtoken API, a different package) — this view would not run as-is if
    it were ever wired up.
    """
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
    """Plain ViewSet, not ModelViewSet — every action is implemented by hand
    (queryset/serializer wiring, pagination, etc. that ModelViewSet would
    normally give for free are all absent here). basename="user" has to be
    passed explicitly at router registration in users/urls.py because of
    this (see comment there).
    """
    permission_classes = []
    serializer_class = UserSerializer

    def get_permissions(self):
        """Per-action permission mapping — DRF calls this once per request
        instead of reading a static `permission_classes` list, which is what
        lets each action require a different Django model permission (see
        permissions.py). Falls through to permission_classes = [] (i.e. no
        permission required) for any action not listed here.
        """
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
        """Creates a user and adds it to the auth.Group matching `role`
        (admin/moderator/user — see migration 0002_create_default_groups,
        which must have run or Group.objects.get() below raises
        DoesNotExist).

        Two known rough edges, left as-is:
        - validate_password() runs before user.save(); a weak/common
          password raises Django's ValidationError, which nothing here
          catches, so it surfaces as an unhandled 500 instead of a clean 400.
        - user.save() happens before the Group lookup, with no
          transaction.atomic() wrapping the two — if the group lookup ever
          fails again, the User row is still committed even though the
          request returns 500 (i.e. a user can exist with no group).
        """
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
        # Returns the full queryset unpaginated — REST_FRAMEWORK's
        # DEFAULT_PAGINATION_CLASS/PAGE_SIZE (settings.py) don't apply here,
        # since that's wired through GenericAPIView.paginate_queryset(),
        # which this hand-rolled action never calls.
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
        # NB: CanUpdateUser always denies (see permissions.py) — this action
        # is effectively unreachable via the API today regardless of caller.
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
        # Same CanPartialUpdateUser issue as update() above.
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
