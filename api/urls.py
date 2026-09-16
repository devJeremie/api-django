"""
Configuration URL du projet
"""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# No django.contrib.admin route here — the admin app is installed
# (INSTALLED_APPS) but not wired up, so /admin/ 404s by design.
urlpatterns = [
    path('', include("users.urls")),

    # OpenAPI schema (raw JSON) and the interactive Swagger UI built on top
    # of it. UI is at /api/, not /api/swagger-ui — the view name is
    # "swagger-ui" but the URL path is just "api/".
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # JWT issuing/refresh (simplejwt), independent of users.views.UserLoginView
    # (which exists but is never routed — see that file).
    path("login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refreshtoken", TokenRefreshView.as_view(), name="token_refresh"),
]
