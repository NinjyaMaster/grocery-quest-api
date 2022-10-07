"""
Views for the user API
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import ErrorDetail

from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.conf import settings
from django.utils.encoding import (
                                    smart_str,
                                    smart_bytes,
                                    DjangoUnicodeDecodeError
)
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from .renderers import UserRenderer

from .serializers import (
                            RegisterSerializer,
                            LoginSerializer,
                            EmailVerificationSerializer,
                            UserSerializer,
                            RequestPasswordResetSerializer,
                            SetNewPasswordSerializer
)

from .utils import Util

import jwt


def send_verification_email(request):
    user = get_user_model().objects.get(email=request.data['email'])
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


class RegisterView(generics.GenericAPIView):
    """Register user"""
    serializer_class = RegisterSerializer
    renderer_classes = (UserRenderer, )

    def post(self, request):
        """Create new user"""
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            if 'email' in errors and \
                    'email already exists' in errors['email'][0]:
                send_verification_email(request)
                return Response(
                    {
                        'email': [ErrorDetail(
                            string='user with this email already exists.',
                            code='unique'
                            )]
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        user_data = serializer.data
        send_verification_email(request)

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


class RequestPasswordResetEmail(generics.GenericAPIView):
    """Request password reset"""
    serializer_class = RequestPasswordResetSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data) # noqa

        email = request.data.get('email', '')

        if get_user_model().objects.filter(email=email).exists():
            user = get_user_model().objects.get(email=email)
            uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            current_site = get_current_site(request=request).domain
            relativeLink = reverse(
                                    'user:validate-password-reset',
                                    kwargs={'uidb64': uidb64, 'token': token}
                                )
            redirect_url = request.data.get('redirect_url', '')
            absurl = 'http://'+current_site + relativeLink
            email_body = 'Hello, \n' + \
                'Use link below to reset your password  \n' + \
                absurl+"?redirect_url="+redirect_url
            data = {
                'email_body': email_body,
                'email_to': [user.email],
                'email_subject': 'Reset your passsword'
                }

            Util.send_email(data)
            return Response(
                {'success': 'We have sent you a link to reset your password'},
                status=status.HTTP_200_OK
                )
        else:
            return Response(
                {'fail': 'The email is not registered'},
                status=status.HTTP_400_BAD_REQUEST
                )


class ValidatePasswordResetEmail(generics.GenericAPIView):
    """Validate Password reset email """
    serializer_class = SetNewPasswordSerializer

    def get(self, request, uidb64, token):

        # use redirect_url once react web site is activated
        # redirect_url = request.GET.get('redirect_url')

        try:
            id = smart_str(urlsafe_base64_decode(uidb64))
            user = get_user_model().objects.get(id=id)

            if not PasswordResetTokenGenerator().check_token(user, token):
                return Response(
                    {'error': 'Token is not valid, please request a new one'},
                    status=status.HTTP_401_UNAUTHORIZED
                    )

            return Response({
                        'success': True,
                        'message': 'Credentials Valid',
                        'uidb64': uidb64,
                        'token': token
                        },
                        status=status.HTTP_200_OK
                    )

        except DjangoUnicodeDecodeError as identifier: # noqa
            return Response(
                {'error': 'Token is not valid, please request a new one'}
                )


class CompletePasswordReset(generics.GenericAPIView):
    """Validate & Save new password"""
    serializer_class = SetNewPasswordSerializer

    def patch(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {'success': True, 'message': 'Password reset success'},
            status=status.HTTP_200_OK
            )
