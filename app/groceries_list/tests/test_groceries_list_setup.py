"""
Setup for the groceries_list API test.
"""
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from core.models import Store


class GroceriesAPITestSetup(APITestCase):

    def setUp(self):
        self.stores_url = reverse('groceries_list:stores')

        self.user_data = {
            'email': 'email@gamil.com',
            'username': 'testname',
            'password': 'testpassword',
        }
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    def create_user(self):
        """Create and return user."""
        user = get_user_model().objects.create_user(
            email="email@gamil.com",
            password="testname",
            username="testpassword"
        )
        user.is_verified = True
        self.client.force_authenticate(user)

        return user

    def store_detail_url(store_id):
        """Create and return a store detail URL."""
        return reverse('groceries_list:store', args=[store_id])

    def create_store(self, owner, name):
        """Create and return a sample store."""
        store = Store.objects.create(owner=owner, name=name)
        return store
