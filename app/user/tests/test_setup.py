"""
Setup for the user API test.
"""
from rest_framework.test import APITestCase
from django.urls import reverse


class UserAPITestSetup(APITestCase):

    def setUp(self):
        self.register_url = reverse('user:register')
        # self.login_url = reverse('login')

        self.user_data = {
            'email': 'email@gamil.com',
            'username': 'username1',
            'password': 'testpassword',
        }

        self.duplicate_email_user_data = {
            'email': 'email@gamil.com',
            'username': 'username2',
            'password': 'testpassword',
        }

        self.duplicate_username_user_data = {
            'email': 'email2@gamil.com',
            'username': 'username1',
            'password': 'testpassword',
        }

        return super().setUp()

    def tearDown(self):
        return super().tearDown()