"""
Serializers for the user API View.
"""
from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed

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
        """Validate the user"""
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
                'Not Valid Email: ' + str(e)
            )

        return attrs

    def create(self, validated_data):
        """Create amd return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)


class EmailVerificationSerializer(serializers.ModelSerializer):
    """Selializer for email verification"""
    token = serializers.CharField(max_length=555)

    class Meta:
        model = get_user_model()
        fields = ['token']


class LoginSerializer(serializers.Serializer):
    """Selializer for login/authentification and return tokens"""
    email = serializers.EmailField(max_length=255, min_length=3)
    password = serializers.CharField(
        max_length=68,
        min_length=6,
        write_only=True,
        trim_whitespace=False,
    )
    username = serializers.CharField(
        max_length=255,
        min_length=3,
        read_only=True
    )
    tokens = serializers.SerializerMethodField()

    def get_tokens(self, obj):
        user = get_user_model().objects.get(email=obj['email'])
        return {
            'refresh': user.tokens()['refresh'],
            'access': user.tokens()['access']
        }

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'username', 'tokens']

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            request=self.context.get('requet'),
            username=email,
            password=password
        )

        if not user:
            raise AuthenticationFailed('Invalid credentials, try again')
        if not user.is_active:
            raise AuthenticationFailed('Account disabled, contact admin')
        if not user.is_verified:
            raise AuthenticationFailed('Email is not verified')

        return {
            'email': user.email,
            'username': user.username,
            'tokens': user.tokens
        }
