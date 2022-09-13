"""
Serializers for the user API View.
"""
from django.contrib.auth import get_user_model
from rest_framework import serializers

from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class RegisterSerializer(serializers.ModelSerializer):
    """Selializer for new user regstraion"""
    password = serializers.CharField(
                                    max_length=68,
                                    min_length=6,
                                    write_only=True
                                    )

    class Meta:
        model = get_user_model()
        fields = ['email', 'username', 'password']

    def validate(self, attrs):
        email = attrs.get('email', '')
        username = attrs.get('username', '')

        if not username.isalnum():
            raise serializers.ValidationError(
                'The username should only contain alphanumetric characters'
                )

        try:
            validate_email(email)
        except ValidationError as e:
            raise serializers.ValidationError(
                'Not Valid Email: ' + e
            )

        return attrs

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)
