"""
Configuration URL du projet
"""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# Aucune route django.contrib.admin ici — l'app admin est installée
# (INSTALLED_APPS) mais non câblée, donc /admin/ renvoie 404 volontairement.
urlpatterns = [
    path('', include("users.urls")),

    # Schéma OpenAPI (JSON brut) et l'UI Swagger interactive construite
    # par-dessus. L'UI est sur /api/, pas /api/swagger-ui — le nom de la
    # vue est "swagger-ui" mais le chemin d'URL est juste "api/".
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

    # Émission/rafraîchissement JWT (simplejwt), indépendant de
    # users.views.UserLoginView (qui existe mais n'est jamais routée — voir ce fichier).
    path("login", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refreshtoken", TokenRefreshView.as_view(), name="token_refresh"),
]
