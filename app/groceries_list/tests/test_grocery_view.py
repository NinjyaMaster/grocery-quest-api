"""
Tests for the grocery API.
"""
from rest_framework import status # noqa

from core.models import Grocery # noqa
from groceries_list.serializers import GrocerySerializer # noqa

from .test_groceries_list_setup import GroceriesListAPITestSetup


class GroceryAPITests(GroceriesListAPITestSetup):

    def test_auth_required(self):
        """Test auth is required to call API."""
        pass
