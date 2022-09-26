"""
Tests for the user API.
"""
from .test_setup import UserAPITestSetup
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core import mail
from django.utils.encoding import smart_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode

from rest_framework import status


class PasswordResetTests(UserAPITestSetup):
    """Test Password reset"""

    def test_request_password_reset_with_unregistered_email_error(self):
        """
        Test error returned when user request password reset
        with unregistered email
        """
        payload = {
            'email': 'bad@bademail.com',
        }
        res = self.client.post(
            self.request_password_reset_url,
            payload,
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_request_password_reset_with_registered_email_success(self):
        """
        Test email token successfully when user request password reset with
        registered email
        """
        self.create_user()

        payload = {
            'email': self.user_data['email'],
        }
        res = self.client.post(
            self.request_password_reset_url,
            payload,
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, 'Reset your passsword')

    def test_validate_password_reset_email_with_bad_token_error(self):
        """
        Test error returned when validate resetting password with bad token
        """
        self.create_user()

        user = get_user_model().objects.get(email=self.user_data['email'])
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = 'BadToken'
        validate_password_reset_url = reverse(
            'user:validate-password-reset',
            kwargs={'uidb64': uidb64, 'token': token}
        )
        res = self.client.get(
            validate_password_reset_url
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_validate_password_reset_email_with_right_token_success(self):
        """
        Test validate password reset email token successfully with
        good crediential
        """
        self.create_user()

        user = get_user_model().objects.get(email=self.user_data['email'])
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        validate_password_reset_url = reverse(
            'user:validate-password-reset',
            kwargs={'uidb64': uidb64, 'token': token}
        )
        res = self.client.get(
            validate_password_reset_url
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_complete_password_reset_with_invalid_password_error(self):
        """
        Test error returned when resetting password with bad password
        """
        self.create_user()

        user = get_user_model().objects.get(email=self.user_data['email'])
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        payload = {
            'password': 'a',
            'token': token,
            'uidb64': uidb64
        }
        res = self.client.patch(
            self.complete_password_reset_url,
            payload
        )
        user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_complete_password_reset_wth_invalid_crediential_error(self):
        """
        Test error returned when resetting password with bad crediential
        """
        self.create_user()

        user = get_user_model().objects.get(email=self.user_data['email'])
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user) # noqa
        payload = {
            'password': 'newpassword',
            'token': 'badtoken',
            'uidb64': uidb64
        }
        res = self.client.patch(
            self.complete_password_reset_url,
            payload
        )
        user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_complete_password_reset_with_good_credientials_success(self):
        """
        Test complete password reset successfully
        """
        self.create_user()

        user = get_user_model().objects.get(email=self.user_data['email'])
        uidb64 = urlsafe_base64_encode(smart_bytes(user.id))
        token = PasswordResetTokenGenerator().make_token(user)
        payload = {
            'password': 'newpassword',
            'token': token,
            'uidb64': uidb64
        }
        res = self.client.patch(
            self.complete_password_reset_url,
            payload
        )
        user.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(user.check_password(payload['password']))
