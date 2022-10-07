"""
Tests for the user API.
"""
from .test_setup import UserAPITestSetup
from django.contrib.auth import get_user_model
from django.core import mail

from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken


class UserAPITests(UserAPITestSetup):
    """Test the register/login of the user API."""

    def test_user_register_with_no_data_error(self):
        """Test error returned if user register with no data."""
        res = self.client.post(self.register_url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_register_success(self):
        """Test registering a user is successful."""
        res = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )

        self.assertEqual(res.data['email'], self.user_data['email'])
        self.assertEqual(res.data['username'], self.user_data['username'])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Verify your email')

    def test_user_register_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        res = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Verify your email')

        non_unique_email_user_data = self.user_data.copy()
        non_unique_email_user_data['username'] = 'different'

        res = self.client.post(
            self.register_url,
            non_unique_email_user_data,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, 'Verify your email')

    def test_user_register_with_username_exists_error(self):
        """Test error returned if user with username exists."""
        res = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        non_unique_username_user_data = self.user_data.copy()
        non_unique_username_user_data['email'] = 'different@different.com'

        res = self.client.post(
            self.register_url,
            non_unique_username_user_data,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_register_with_bad_email_error(self):
        """Test error returned if email is not valid."""
        self.user_data["email"] = "this is bad email"
        res = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_cannot_login_with_unverified_email(self):
        """Test error returned if user login with un-verified email"""
        self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Verify your email')

        res = self.client.post(
            self.login_url,
            self.user_data,
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, 'Verify your email')
        self.assertEqual(mail.outbox[1].to[0], self.user_data['email'])

    def test_user_can_login_with_verified_email(self):
        """Test success returned if user login with verified email"""
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )
        email = response.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        res = self.client.post(
            self.login_url,
            self.user_data,
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', res.data)

    def test_user_cannot_login_with_bad_credentials(self):
        """Test error returned if credentials is invalid"""
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )
        email = response.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        bad_credential_user_data = self.user_data.copy()
        bad_credential_user_data['password'] = 'badpassword'
        res = self.client.post(
            self.login_url,
            bad_credential_user_data,
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_receive_token_for_user(self):
        """Test user receive token when login"""
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )
        email = response.data['email']
        user = get_user_model().objects.get(email=email)
        user.is_verified = True
        user.save()
        res = self.client.post(
            self.login_url,
            self.user_data,
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', res.data)

    def test_verify_email_with_token(self):
        """Test success returned if user verify email with correct token"""
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        email = response.data['email']
        user = get_user_model().objects.get(email=email)
        token = RefreshToken.for_user(user).access_token
        verifyemail_with_token = self.verifyemail_url + "?token=" + str(token)

        res = self.client.get(verifyemail_with_token)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_verify_email_with_wrong_token(self):
        """Test error returned if user verify email with wrong token"""
        response = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        verifyemail_with_token = self.verifyemail_url + "?token=wrongtoken"

        res = self.client.get(verifyemail_with_token)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
