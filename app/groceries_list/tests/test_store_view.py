"""
Tests for the store API.
"""
from rest_framework import status

from core.models import Store
from groceries_list.serializers import (
                                        StoresListSerializer,
                                        StoreDetailSerializer
                    )

from .test_groceries_list_setup import GroceriesListAPITestSetup


class StoreAPITests(GroceriesListAPITestSetup):

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(self.stores_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_stores(self):
        """Test retrieving a list of stores."""
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "Target"
                    }
        self.create_store(**store_data)
        res = self.client.get(self.stores_url)
        stores = Store.objects.all().order_by('-id')
        serializer = StoresListSerializer(stores, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_stores_list_limited_to_user(self):
        """Test list of stores is limited to authenticated user."""
        other_user_data = {
                            'email': 'other@example.com',
                            'password': 'otherpassword',
                            'username': 'otherusername'
                        }
        other_user = self.create_user(**other_user_data)
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "Target"
                    }
        other_store_data = {
                        'owner': other_user,
                        'name': "whole Foods"
                    }
        self.create_store(**store_data)
        self.create_store(**other_store_data)
        res = self.client.get(self.stores_url)
        stores = Store.objects.filter(owner=user)
        serializer = StoresListSerializer(stores, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_store_detail(self):
        """Test get store detail."""
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "Target"
                    }
        store = self.create_store(**store_data)
        store_detail_url = self.store_detail_url(store.id)
        res = self.client.get(store_detail_url)
        serializer = StoreDetailSerializer(store)
        self.assertEqual(res.data, serializer.data)
