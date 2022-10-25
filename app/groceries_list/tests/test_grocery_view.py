"""
Tests for the grocery API.
"""
from rest_framework import status

from core.models import Grocery # noqa
from groceries_list.serializers import GrocerySerializer # noqa

from .test_groceries_list_setup import GroceriesListAPITestSetup


class GroceryAPITests(GroceriesListAPITestSetup):

    def test_auth_required(self):
        """Test auth is required to call API."""
        user = self.create_user()
        grocery_data = {
            'owner': user,
            'name': 'Tomato'
        }
        grocery = self.create_grocery(**grocery_data)
        self.client.logout()
        res = self.client.get(self.grocery_detail_url(grocery.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
