"""
Tests for the user API.
"""
from .test_setup import UserAPITestSetup


class UserAPITests(UserAPITestSetup):
    """Test the register/login of the user API."""

    def test_user_register_with_no_data_error(self):
        """Test error returned if user register with no data."""
        res = self.client.post(self.register_url)

        self.assertEqual(res.status_code, 400)

    def test_user_register_success(self):
        """Test registering a user is successful."""
        res = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )

        self.assertEqual(res.data['email'], self.user_data['email'])
        self.assertEqual(res.data['username'], self.user_data['username'])
        self.assertEqual(res.status_code, 201)

    def test_user_register_with_email_exists_error(self):
        """Test error returned if user with email exists."""
        res = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )
        self.assertEqual(res.status_code, 201)

        res = self.client.post(
            self.register_url,
            self.duplicate_email_user_data,
            format="json",
        )
        self.assertEqual(res.status_code, 400)

    def test_user_register_with_username_exists_error(self):
        """Test error returned if user with username exists."""
        res = self.client.post(
            self.register_url,
            self.user_data,
            format="json",
        )
        self.assertEqual(res.status_code, 201)

        res = self.client.post(
            self.register_url,
            self.duplicate_username_user_data,
            format="json",
        )
        self.assertEqual(res.status_code, 400)
