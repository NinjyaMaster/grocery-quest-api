"""
Serializers for MyProfile APIs
"""
from rest_framework import serializers

from django.contrib.auth import get_user_model


from core.models import (
    MyProfile
)


class FriendSerializer(serializers.ModelSerializer):
    """Serializer for MyProfile Friend"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'username', 'email']
        read_only_fields = ['id', 'username', 'email']


class MyProfileSerializer(serializers.ModelSerializer):
    """Serializer for Store."""
    friends = FriendSerializer(many=True, required=False)

    class Meta:
        model = MyProfile
        fields = ['id', 'friends']
        read_only_fields = ['id']
