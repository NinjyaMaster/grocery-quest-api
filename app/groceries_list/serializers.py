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

    class Meta:
        model = Grocery
        fields = ['id', 'name']
        read_only_fields = ['id']


class StoreDetailSerializer(serializers.ModelSerializer):
    """Serializer for Store."""
    groceries = GrocerySerializer(many=True, required=False)

    class Meta:
        model = Store
        fields = ['id', 'name', 'groceries']
        read_only_fields = ['id']


class StoresListSerializer(serializers.ModelSerializer):
    """Serializer for Stores List."""

    class Meta:
        model = Store
        fields = ['id', 'name']
        read_only_fields = ['id']
