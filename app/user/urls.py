"""
URL mappings for the user API.
"""
from django.urls import path

from user import views

from rest_framework_simplejwt.views import (
    TokenRefreshView,
)


app_name = 'user'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path(
            'verify-email/',
            views.VerifyEmailView.as_view(),
            name='verify-email'
        ),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
