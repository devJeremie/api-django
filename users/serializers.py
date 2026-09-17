# from django.contrib.auth.models import User
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Représentation lecture/écriture utilisée pour les réponses list/retrieve/update.

    Pas de champ `password` — c'est intentionnel (ne jamais renvoyer les données
    de mot de passe), mais cela signifie aussi que UserSerializer ne peut pas
    servir à définir un mot de passe ; c'est géré séparément dans
    UserViewSet.create() via set_password().
    """
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "role",
            "date_joined",
            "last_login",
        ]


class UserCreationSerializer(serializers.ModelSerializer):
    """Forme d'entrée documentée pour POST /users/ dans le schéma OpenAPI
    (utilisée via @extend_schema dans views.py) — UserViewSet.create()
    n'instancie/ne valide PAS réellement via ce serializer, il construit
    un simple User(**request.data) à la place. Garder les deux synchronisés
    manuellement si l'un des deux change.
    """
    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
            "first_name",
            "last_name",
            "role",
        ]

    extra_kwargs = {
        "username":{"required": True},
        "password":{"required": True},
        "email":{"required": True},
        "role":{"default": User.USER},
    }


class UserLoginSerializer(serializers.ModelSerializer):
    # BUG : model/fields/extra_kwargs doivent être définis dans une classe
    # `class Meta` imbriquée pour qu'un ModelSerializer les prenne en compte —
    # tel qu'écrit, cette classe ne déclare aucun champ, donc is_valid()
    # passerait sans réellement exiger username/password. Sans conséquence
    # actuellement car le seul consommateur, UserLoginView (views.py), n'est
    # câblé dans aucune urlpatterns — corriger ceci si cette vue est un jour réactivée.
    model = User
    fields = [
        "username",
        "password",
    ]
    extra_kwargs = {
        "username":{"required": True},
        "password":{"required": True},
    }
