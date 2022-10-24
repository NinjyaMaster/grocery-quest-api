"""
Tests for the store API.
"""
from django.contrib.auth import get_user_model

from rest_framework import status

from core.models import Store
from groceries_list.serializers import StoreSerializer

from .test_groceries_list_setup import GroceriesAPITestSetup


def create_user(
                email='user@example.com',
                password='testpass123',
                username='testusername'):
    """Create and return user."""
    return get_user_model().objects.create_user(
                                            email=email,
                                            password=password,
                                            username=username)


class StoreAPITests(GroceriesAPITestSetup):

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(self.stores_url)
        print(self.stores_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_stores(self):
        """Test retrieving a list of stores."""
        user = self.create_user()

        self.create_store(user, "Target")

        res = self.client.get(self.stores_url)

        stores = Store.objects.all().order_by('-id')
        serializer = StoreSerializer(stores, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
