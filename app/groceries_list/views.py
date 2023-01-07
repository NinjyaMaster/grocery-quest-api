"""
Views for the goroceries API
"""
from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import permissions
from rest_framework.generics import (
                                        ListCreateAPIView,
                                        RetrieveUpdateDestroyAPIView,
                                        CreateAPIView
)
from rest_framework import status

from .permissions import IsOwner
from .serializers import (
                            StoreDetailSerializer,
                            StoresListSerializer,
                            GrocerySerializer
    )
from core.models import (
    Store,
    Grocery
)


class StoreListAPIView(ListCreateAPIView):
    """Retrive Store List"""
    serializer_class = StoresListSerializer
    queryset = Store.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class StoreDetailAPIView(RetrieveUpdateDestroyAPIView):
    """View for retrive and delete Store"""
    serializer_class = StoreDetailSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = Store.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        """Retrieve Store Detail"""
        return self.queryset.filter(owner=self.request.user)

    def delete(self, request, *args, **kwargs):
        """Delete Store detail and Grocery that has the store_id"""
        store_id = kwargs['id']
        store = get_object_or_404(Store, pk=store_id)
        store.delete()
        groceries = Grocery.objects.filter(Q(store_id=store_id))
        for grocery in groceries:
            grocery.delete()
        return Response(data={'id': store_id}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        """Put/Update Store Detail. Copy patch method"""
        res = self.partial_update(request, *args, **kwargs)
        return res

    def partial_update(self, request, *args, **kwargs):
        """Patch Store Detail. when Store is completed,
        flag all the groceries to completed"""
        data = request.data
        store_id = kwargs['id']
        store = get_object_or_404(Store, pk=store_id)

        for key, value in data.items():
            # create new grocery
            if(key == "groceries"):
                for grocery in value:
                    store.groceries.create(
                                        owner=request.user,
                                        name=grocery['name'],
                                        store_id=store_id,
                                        is_completed=False
                                        )
            # set attribute
            else:
                setattr(store, key, value)
        store.save()

        if "is_completed" in data.keys() and data['is_completed']:
            groceries = store.groceries.all()
            if groceries:
                for grocery in groceries:
                    setattr(grocery, 'is_completed', True)
                    grocery.save()

        return Response(
                        data=StoreDetailSerializer(store).data,
                        status=status.HTTP_202_ACCEPTED
                        )


class GroceryCreateAPIView(CreateAPIView):
    """View for create new Grocery"""
    serializer_class = GrocerySerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def post(self, request, *args, **kwargs):
        """Create Grocery and add to the store"""
        data = request.data
        stores = Store.objects.filter(Q(id=data['store_id']))
        if stores:
            store = stores[0]
            grocery = store.groceries.create(
                                            owner=request.user,
                                            name=data['name'],
                                            store_id=data['store_id']
                                        )
            return Response(
                            data=GrocerySerializer(grocery).data,
                            status=status.HTTP_201_CREATED
                            )
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


def is_store_completed(store):
    is_store_completed = True
    groceries = store.groceries.all()
    if not groceries:
        is_store_completed = False
    else:
        for groceryItem in groceries:
            if not groceryItem.is_completed:
                is_store_completed = False

    return is_store_completed


class GroceryDetailAPIView(RetrieveUpdateDestroyAPIView):
    """View for Grocery Detail: put, patch, delete"""
    serializer_class = GrocerySerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = Grocery.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        """Retrive Grocery Detail"""
        return self.queryset.filter(owner=self.request.user)

    def update(self, request, *args, **kwargs):
        """Put/Update Grocery Detail. Copy patch method"""
        res = self.partial_update(request, *args, **kwargs)
        return res

    def partial_update(self, request, *args, **kwargs):
        """Patch Grocery Detail / Check all of the groceries at
        the store are completed. Then turn store in_completed to True"""
        data = request.data
        grocery_id = kwargs['id']
        grocery = get_object_or_404(Grocery, pk=grocery_id)
        for key, value in data.items():
            setattr(grocery, key, value)
        grocery.save()
        store = get_object_or_404(Store, pk=grocery.store_id)
        store_completed = is_store_completed(store)
        setattr(store, "is_completed", store_completed)
        store.save()
        grocery_serialized_data = GrocerySerializer(grocery).data
        grocery_serialized_data['is_store_completed'] = store_completed
        return Response(
                        data=grocery_serialized_data,
                        status=status.HTTP_202_ACCEPTED
                        )

    def delete(self, request, *args, **kwargs):
        """Delete Grocery obj / Check all od the groceries
        at the store are completed"""
        grocery_id = kwargs['id']
        grocery = get_object_or_404(Grocery, pk=grocery_id)
        store = get_object_or_404(Store, pk=grocery.store_id)
        grocery.delete()
        store_completed = is_store_completed(store)
        if store.is_completed != store_completed:
            setattr(
                    store,
                    "is_completed",
                    is_store_completed(store)
                    )
            store.save()

        return Response(status=status.HTTP_200_OK)
