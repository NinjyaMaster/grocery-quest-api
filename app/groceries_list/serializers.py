"""
Serializers for groceries APIs
"""
from rest_framework import serializers

from core.models import (
    Store,
    Grocery
)


class GrocerySerializer(serializers.ModelSerializer):
    """Serializer for Grocery"""
    store_id = serializers.IntegerField()

    class Meta:
        model = Grocery
        fields = ['id', 'name', 'qty', 'store_id', 'is_completed']
        read_only_fields = ['id']


class StoreDetailSerializer(serializers.ModelSerializer):
    """Serializer for Store."""
    groceries = GrocerySerializer(many=True, required=False)

    class Meta:
        model = Store
        fields = ['id', 'name', 'groceries', 'is_completed']
        read_only_fields = ['id']


class StoresListSerializer(serializers.ModelSerializer):
    """Serializer for Stores List."""
    groceries = GrocerySerializer(many=True, required=False)

    class Meta:
        model = Store
        fields = ['id', 'name', 'groceries', 'is_completed']
        read_only_fields = ['id']

    def create(self, validated_data):
        user = self.context['request'].user
        if 'groceries' not in validated_data:
            groceries_data = {}
        else:
            groceries_data = validated_data.pop('groceries')

        store = Store.objects.create(**validated_data)
        for grocery_data in groceries_data:
            grocery_data['store_id'] = store.id
            grocery = Grocery.objects.create(owner=user, **grocery_data)
            store.groceries.add(grocery)

        return store
