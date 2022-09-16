"""
URL mappings for the user API.
"""
from django.urls import path

from user import views


app_name = 'user'

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path(
            'verify-email/',
            views.VerifyEmailView.as_view(),
            name='verify-email'
        ),
]