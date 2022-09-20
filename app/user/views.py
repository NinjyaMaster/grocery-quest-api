"""
Views for the user API
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from .renderers import UserRenderer

from .serializers import (
                            RegisterSerializer,
                            LoginSerializer,
                            EmailVerificationSerializer,
                            UserSerializer
)

from .utils import Util

import jwt


class RegisterView(generics.GenericAPIView):
    """Register user"""
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer, )

    def post(self, request):
        """Create new user"""
        user = request.data
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        user = get_user_model().objects.get(email=user_data['email'])

        token = RefreshToken.for_user(user).access_token
        current_site = get_current_site(request).domain
        relativeLink = reverse('user:verify-email')
        absurl = 'http://'+current_site + relativeLink + "?token=" + str(token)
        email_body = 'Hi '+user.username +  \
            ' Use link below to verify your email \n' \
            + 'domain: ' + absurl
        data = {
            'domain': absurl,
            'email_subject': 'Verify your email',
            'email_body': email_body,
            'email_to': [user.email]
            }

        Util.send_email(data)

        return Response(user_data, status=status.HTTP_201_CREATED)


class VerifyEmailView(generics.GenericAPIView):
    """Verify Email"""
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        """Verify Email or Send Verification Error"""
        token = request.GET.get('token')
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms='HS256'
            )
            user = get_user_model().objects.get(id=payload['user_id'])
            if not user.is_verified:
                user.is_verified = True
                user.save()
            return Response(
                {'email': 'Successfully activated'},
                status=status.HTTP_200_OK
            )

        except jwt.ExpiredSignatureError as identifier: # noqa
            # Write code to issue new token
            return Response(
                {'error': 'Activation Expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError as identifier: # noqa
            return Response(
                {'error': 'Invalid Token'},
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginAPIView(generics.GenericAPIView):
    """Authenticate and return tokens for user"""
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrieve and return the authenticated user"""
        return self.request.user
