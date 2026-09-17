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
    """Code mort : non enregistré dans aucun urls.py (api/urls.py ou users/urls.py).
    La connexion JWT passe en réalité par le TokenObtainPairView de simplejwt
    sur /login. Laissé ici depuis une itération précédente ; dépend aussi de
    UserLoginSerializer, qui a son propre bug (voir serializers.py), et de
    rest_framework_simplejwt.tokens.Token, qui ne fournit pas l'API
    Token.objects.get_or_create(...) utilisée ci-dessous (c'est l'API
    authtoken de DRF, un package différent) — cette vue ne fonctionnerait
    pas telle quelle si elle était un jour câblée.
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
    """Simple ViewSet, pas ModelViewSet — chaque action est implémentée à la
    main (le câblage queryset/serializer, la pagination, etc. que ModelViewSet
    fournirait normalement gratuitement sont tous absents ici). basename="user"
    doit être passé explicitement lors de l'enregistrement du router dans
    users/urls.py à cause de cela (voir le commentaire à cet endroit).
    """
    permission_classes = []
    serializer_class = UserSerializer

    def get_permissions(self):
        """Mappage des permissions par action — DRF appelle ceci une fois par
        requête au lieu de lire une liste statique `permission_classes`, ce
        qui permet à chaque action d'exiger une permission de modèle Django
        différente (voir permissions.py). Retombe sur permission_classes = []
        (c.-à-d. aucune permission requise) pour toute action non listée ici.
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
        """Crée un utilisateur et l'ajoute à l'auth.Group correspondant à
        `role` (admin/moderator/user — voir la migration
        0002_create_default_groups, qui doit avoir été exécutée sinon
        Group.objects.get() ci-dessous lève DoesNotExist).

        Deux points connus laissés tels quels :
        - validate_password() s'exécute avant user.save() ; un mot de passe
          faible/courant lève une ValidationError de Django, que rien ici
          n'intercepte, donc cela remonte comme un 500 non géré au lieu d'un
          400 propre.
        - user.save() a lieu avant la recherche du Group, sans
          transaction.atomic() englobant les deux — si la recherche du
          groupe échoue à nouveau, la ligne User est quand même validée même
          si la requête renvoie 500 (c.-à-d. qu'un utilisateur peut exister
          sans groupe).
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

            else: # Le rôle de l'utilisateur est USER
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
        # Renvoie le queryset complet sans pagination — les DEFAULT_PAGINATION_CLASS/
        # PAGE_SIZE de REST_FRAMEWORK (settings.py) ne s'appliquent pas ici,
        # car cela passe par GenericAPIView.paginate_queryset(), que cette
        # action écrite à la main n'appelle jamais.
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
        # NB : CanUpdateUser refuse toujours (voir permissions.py) — cette
        # action est aujourd'hui effectivement inatteignable via l'API, quel que soit l'appelant.
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
        # Même problème CanPartialUpdateUser que update() ci-dessus.
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
