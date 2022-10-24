from django.urls import path
from . import views

app_name = 'groceries_list'

urlpatterns = [
    path('', views.StoreListAPIView.as_view(), name="stores"),
    path('<int:id>', views.StoreDetailAPIView.as_view(), name="store"),
    path('grocery/<int:id>', views.GroceryAPIView.as_view(), name='grocery')
]
