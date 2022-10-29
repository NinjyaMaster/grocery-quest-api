"""
Tests for the grocery API.
"""
from rest_framework import status

from .test_groceries_list_setup import GroceriesListAPITestSetup


class GroceryAPITests(GroceriesListAPITestSetup):

    def test_auth_required(self):
        """Test auth is required to call API."""
        user = self.create_user()
        grocery_data = {
            'owner': user,
            'name': 'Tomato',
            'store_id': 1
        }
        grocery = self.create_grocery(**grocery_data)
        self.client.logout()
        res = self.client.get(self.grocery_detail_url(grocery.id))
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_grocery_error(self):
        """Test create grocery without store"""
        self.create_user()
        payload = {
            'name': 'Tomato',
            'store_id': 1
        }
        res = self.client.post(
            self.grocery_url,
            payload,
            format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_add_grocery_to_store_success(self):
        """Test adding grocery to a store."""
        self.create_user()
        store_data = {
            'name': 'lululemon'
        }
        res_store = self.client.post(self.stores_url, store_data)
        self.assertEqual(res_store.status_code, status.HTTP_201_CREATED)
        grocery_data = {
            'name': 'Tomato',
            'store_id': res_store.data['id']
        }
        res_grocery = self.client.post(
            self.grocery_url,
            grocery_data,
            format="json"
        )
        self.assertEqual(res_grocery.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res_grocery.data['store_id'], res_store.data['id'])
        self.assertEqual(res_grocery.data['name'], grocery_data['name'])
        store_url = self.store_detail_url(res_store.data['id'])
        new_store = self.client.get(store_url)
        for key, value in new_store.data['groceries'][0].items():
            if key in grocery_data.keys():
                self.assertEqual(value, grocery_data[key])

    def test_update_grocery_at_store_success(self):
        """Test partial update. Also,check the store is also complete
        when the all groceries are completed"""
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "Target"
                    }
        store = self.create_store(**store_data)
        grocery_data = {
            'owner': user,
            'name': 'Onion',
            'store_id': store.id
        }
        grocery = self.create_grocery(**grocery_data)
        store.groceries.add(grocery)
        new_grocery_data = {
            'is_completed': True,
            'name': 'Onion Ring'
        }
        grocery_detail_url = self.grocery_detail_url(grocery.id)
        grocery_res = self.client.put(
            grocery_detail_url,
            new_grocery_data,
            format="json"
        )
        self.assertEqual(
                        grocery_res.status_code,
                        status.HTTP_202_ACCEPTED
                        )
        for key, value in grocery_res.data.items():
            if key in new_grocery_data.keys():
                self.assertEqual(value, new_grocery_data[key])
        self.assertTrue(grocery_res.data['is_store_completed'])

        store_res = self.client.get(self.store_detail_url(store.id))
        self.assertTrue(store_res.data['is_completed'])

    def test_incompleted_store_with_multiple_groceries(self):
        """Test check the store return incomplete
        when some groceries are incompleted"""
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "Target"
                    }
        store = self.create_store(**store_data)
        grocery_data = {
            'owner': user,
            'name': 'Onion',
            'store_id': store.id
        }
        grocery = self.create_grocery(**grocery_data)
        store.groceries.add(grocery)
        other_grocery_data = {
            'owner': user,
            'name': 'Banana',
            'store_id': store.id
        }
        other_grocery = self.create_grocery(**other_grocery_data)
        store.groceries.add(other_grocery)

        new_grocery_data = {
            'is_completed': True,
            'name': 'Onion Ring'
        }
        grocery_detail_url = self.grocery_detail_url(grocery.id)
        grocery_res = self.client.put(
            grocery_detail_url,
            new_grocery_data,
            format="json"
        )
        self.assertFalse(grocery_res.data['is_store_completed'])
        store_res = self.client.get(self.store_detail_url(store.id))
        self.assertFalse(store_res.data['is_completed'])

    def test_delete_grocery_at_store_success(self):
        """Test deletting grocery.Store that doesn't have
        any grocery has is_completed=False flag """
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "Target"
                    }
        store = self.create_store(**store_data)
        grocery = store.groceries.create(
                                        owner=user,
                                        name="Tomato",
                                        store_id=store.id
                                        )
        grocery_url = self.grocery_detail_url(grocery.id)
        grocery_res = self.client.delete(grocery_url)
        self.assertEqual(grocery_res.status_code, status.HTTP_200_OK)

        store_res = self.client.get(self.store_detail_url(store.id))
        self.assertEqual(len(store_res.data['groceries']), 0)
        self.assertFalse(store_res.data['is_completed'])
        grocery_res = self.client.get(grocery_url)
        self.assertEqual(grocery_res.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_grocery_with_completed_store(self):
        """Test deletting grocery. Store has only compled item."""
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "Target"
                    }
        store = self.create_store(**store_data)
        store.groceries.create(
                                owner=user,
                                name="Tomato",
                                store_id=store.id,
                                is_completed=True
                                )
        other_grocery = store.groceries.create(
                                        owner=user,
                                        name="Wine",
                                        store_id=store.id,
                                        is_completed=False
                                        )
        other_grocery_url = self.grocery_detail_url(other_grocery.id)
        other_grocery_res = self.client.delete(other_grocery_url)
        self.assertEqual(other_grocery_res.status_code, status.HTTP_200_OK)

        store_res = self.client.get(self.store_detail_url(store.id))
        self.assertEqual(len(store_res.data['groceries']), 1)
        self.assertTrue(store_res.data['is_completed'])

    def test_delete_grocery_with_incomplete_store(self):
        """Test deletting grocery. Store has incompleted item."""
        user = self.create_user()
        store_data = {
                        'owner': user,
                        'name': "Target"
                    }
        store = self.create_store(**store_data)
        store.groceries.create(
                                owner=user,
                                name="Tomato",
                                store_id=store.id,
                                is_completed=False
                                )
        other_grocery = store.groceries.create(
                                        owner=user,
                                        name="Wine",
                                        store_id=store.id,
                                        is_completed=False
                                        )
        other_grocery_url = self.grocery_detail_url(other_grocery.id)
        other_grocery_res = self.client.delete(other_grocery_url)
        self.assertEqual(other_grocery_res.status_code, status.HTTP_200_OK)

        store_res = self.client.get(self.store_detail_url(store.id))
        self.assertEqual(len(store_res.data['groceries']), 1)
        self.assertFalse(store_res.data['is_completed'])
