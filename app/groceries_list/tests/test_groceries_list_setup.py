"""
Setup for the groceries_list API test.
"""
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase

from core.models import Store, Grocery


class GroceriesListAPITestSetup(APITestCase):

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

    def create_user(self, **params):
        """Create and return user."""
        defaults = {
            'email': "email@gamil.com",
            'password': "testname",
            'username': "testpassword"
        }
        defaults.update(params)
        user = get_user_model().objects.create_user(**defaults)
        user.is_verified = True
        self.client.force_authenticate(user=user)
        return user

    def store_detail_url(self, store_id):
        """Create and return a store detail URL."""
        return reverse('groceries_list:store', args=[store_id])

    def create_store(self, **params):
        """Create and return a sample store."""
        store = Store.objects.create(**params)
        return store

    def create_grocery(self, **params):
        """Create and return a sample grocery."""
        grocery = Grocery.objects.create(**params)
        return grocery
