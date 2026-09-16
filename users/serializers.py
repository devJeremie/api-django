# from django.contrib.auth.models import User
from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Read/write representation used for list/retrieve/update responses.

    No `password` field — this is intentional (never echo password data back),
    but it also means UserSerializer can't be used to set a password; that's
    handled separately in UserViewSet.create() via set_password().
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
    """Input shape documented for POST /users/ in the OpenAPI schema
    (used via @extend_schema in views.py) — UserViewSet.create() does NOT
    actually instantiate/validate against this serializer, it builds a bare
    User(**request.data) instead. Keep the two in sync manually if either
    changes.
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
    # BUG: model/fields/extra_kwargs must live under a nested `class Meta`
    # for a ModelSerializer to pick them up — as written, this class declares
    # no fields at all, so is_valid() would pass without actually requiring
    # username/password. Currently harmless because the only consumer,
    # UserLoginView (views.py), is not wired into any urlpatterns — fix this
    # if that view is ever revived.
    model = User
    fields = [
        "username",
        "password",
    ]
    extra_kwargs = {
        "username":{"required": True},
        "password":{"required": True},
    }
