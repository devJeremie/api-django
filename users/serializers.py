# from django.contrib.auth.models import User
from rest_framework import serializers

from .models import User

class UserSerializer(serializers.ModelSerializer): 
    class Meta : 
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
    model = User
    fields = [
        "username",
        "password",
    ]
    extra_kwargs = {
        "username":{"required": True},
        "password":{"required": True},
    }