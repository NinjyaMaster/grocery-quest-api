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
    path(
        'request-password-reset/',
        views.RequestPasswordResetEmail.as_view(),
        name='request-password-reset'
        ),
    path(
        'Input-new-password-reset/<uidb64>/<token>/',
        views.ValidatePasswordResetEmail.as_view(),
        name='validate-password-reset'
        ),
    path(
        'complete-password-reset/',
        views.CompletePasswordReset.as_view(),
        name='complete-password-reset'
        )
]
