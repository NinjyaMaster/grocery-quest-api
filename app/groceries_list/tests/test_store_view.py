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

    def test_create_store(self):
        """Test creating a store."""
        user = self.create_user()
        payload = {
            'name': 'lululemon'
        }
        res = self.client.post(self.stores_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        store = Store.objects.get(id=res.data['id'])
        for k, v in payload.items():
            self.assertEqual(getattr(store, k), v)
        self.assertEqual(store.owner, user)

    def test_unauthorized_user_create_store_error(self):
        """Test creating a store fail."""
        payload = {
            'name': 'lululemon'
        }
        res = self.client.post(self.stores_url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_store(self):
        """Test delete store. Also check all grocery
        that has store_id is deleted"""
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "Target"
                    }
        store = self.create_store(**store_data)
        store_detail_url = self.store_detail_url(store.id)
        grocery_data = {
            'owner': user,
            'name': 'Onion',
            'store_id': store.id
        }
        grocery = self.create_grocery(**grocery_data)
        res_delete = self.client.delete(store_detail_url)
        self.assertEqual(
                        res_delete.status_code,
                        status.HTTP_200_OK
                        )

        res_store_detail = self.client.get(store_detail_url)
        self.assertEqual(
                        res_store_detail.status_code,
                        status.HTTP_404_NOT_FOUND
                        )

        grocery_detail_url = self.grocery_detail_url(grocery.id)
        res_grocery_detail = self.client.get(grocery_detail_url)
        self.assertEqual(
                        res_grocery_detail.status_code,
                        status.HTTP_404_NOT_FOUND
                        )

    def test_update_store(self):
        """Test update store name """
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "lulu lemon"
                    }
        store = self.create_store(**store_data)
        store_detail_url = self.store_detail_url(store.id)
        store.groceries.create(
                                owner=user,
                                name="leggins",
                                store_id=store.id,
                                is_completed=False
                                )
        new_store_data = {
            'name': 'Icebraker',
        }
        store_res = self.client.patch(
            store_detail_url,
            new_store_data,
            format="json"
        )
        self.assertEqual(store_res.status_code, status.HTTP_202_ACCEPTED)
        new_store_res = self.client.get(store_detail_url)
        self.assertEqual(new_store_res.status_code, status.HTTP_200_OK)
        for key, value in new_store_data.items():
            self.assertEqual(value, new_store_res.data[key])

    def test_update_store_and_grocery_completed(self):
        """Test update store name/ completed.
        Check all groceries are completed """
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "lulu lemon"
                    }
        store = self.create_store(**store_data)
        store_detail_url = self.store_detail_url(store.id)
        grocery1 = store.groceries.create(
                                owner=user,
                                name="leggins",
                                store_id=store.id,
                                is_completed=False
                                )
        grocery2 = store.groceries.create(
                                owner=user,
                                name="Tank Top",
                                store_id=store.id,
                                is_completed=False
                                )
        new_store_data = {
            'name': 'Icebraker',
            'is_completed': True
        }
        store_res = self.client.patch(
            store_detail_url,
            new_store_data,
            format="json"
        )
        self.assertEqual(store_res.status_code, status.HTTP_202_ACCEPTED)
        new_store_res = self.client.get(store_detail_url)
        self.assertEqual(new_store_res.status_code, status.HTTP_200_OK)
        for key, value in new_store_data.items():
            self.assertEqual(value, new_store_res.data[key])

        grocery1_res = self.client.get(self.grocery_detail_url(grocery1.id))
        grocery2_res = self.client.get(self.grocery_detail_url(grocery2.id))
        self.assertTrue(grocery1_res.data['is_completed'])
        self.assertTrue(grocery2_res.data['is_completed'])
