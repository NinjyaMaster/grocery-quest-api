"""
Serializers for the user API View.
"""
from django.contrib.auth import get_user_model, authenticate

from rest_framework import serializers, status
from rest_framework.exceptions import AuthenticationFailed

from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.tokens import PasswordResetTokenGenerator


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


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'username']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}}

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        return user


class RequestPasswordResetSerializer(serializers.Serializer):
    """Serializer for request password reset"""

    email = serializers.EmailField(min_length=2)
    redirect_url = serializers.CharField(max_length=500, required=False)

    class Meta:
        fields = ['email']


class SetNewPasswordSerializer(serializers.Serializer):
    """Serializer for set new password"""
    password = serializers.CharField(
        min_length=6, max_length=68, write_only=True)
    token = serializers.CharField(
        min_length=1, write_only=True)
    uidb64 = serializers.CharField(
        min_length=1, write_only=True)

    class Meta:
        fields = ['password', 'token', 'uidb64']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            token = attrs.get('token')
            uidb64 = attrs.get('uidb64')

            id = force_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise AuthenticationFailed(
                    'The reset link is invalid',
                    status.HTTP_401_UNAUTHORIZED
                    )

            user.set_password(password)
            user.save()

            return (user)
        except Exception as e: # noqa
            raise AuthenticationFailed(
                'The reset link is invalid',
                status.HTTP_401_UNAUTHORIZED
                )

        return super().validate(attrs)
