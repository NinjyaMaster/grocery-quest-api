"""
Views for the goroceries API
"""
from rest_framework import permissions
from rest_framework.generics import (
                                        ListCreateAPIView,
                                        RetrieveUpdateDestroyAPIView
)

from .permissions import IsOwner
from .serializers import (
                            StoreSerializer
    )
from core.models import (
    Store
)


class StoreListAPIView(ListCreateAPIView):
    serializer_class = StoreSerializer
    queryset = Store.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsOwner,)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)


class StoreDetailAPIView(RetrieveUpdateDestroyAPIView):
    serializer_class = StoreSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    queryset = Store.objects.all()
    lookup_field = "id"

    def get_queryset(self):
        return self.queryset.filter(owner=self.request.user)
