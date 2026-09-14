"""
Configuration URL du projet
"""

from django.urls import include, path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('', include("users.urls")),
    path("login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refreshtoken", TokenRefreshView.as_view(), name="token_refresh"),
]
