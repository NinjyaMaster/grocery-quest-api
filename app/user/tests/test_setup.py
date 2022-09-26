"""
Setup for the user API test.
"""
from rest_framework.test import APITestCase
from django.urls import reverse
from django.contrib.auth import get_user_model # noqa
from django.core import mail

from rest_framework import status


class UserAPITestSetup(APITestCase):

    def setUp(self):
        self.register_url = reverse('user:register')
        self.login_url = reverse('user:login')
        self.verifyemail_url = reverse('user:verify-email')
        self.request_password_reset_url = \
            reverse('user:request-password-reset')
        self.complete_password_reset_url = \
            reverse('user:complete-password-reset')

        self.user_data = {
            'email': 'email@gamil.com',
            'username': 'username1',
            'password': 'testpassword',
        }

        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def create_user(self):
        res = self.client.post(
            self.register_url,
            self.user_data,
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Verify your email')

        return get_user_model().objects.get(email=self.user_data['email'])
