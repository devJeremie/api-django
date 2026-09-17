from django.urls import include, path
from rest_framework import routers

from users import views

router = routers.DefaultRouter()

# basename est requis ici : DefaultRouter l'infère normalement depuis
# viewset.queryset.model, mais UserViewSet est un simple ViewSet (pas
# d'attribut .queryset) puisqu'il interroge User.objects à la main dans
# chaque méthode — l'enregistrement du router échoue avec une AssertionError sans cela.
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),

    # Connexion/déconnexion par session pour l'API navigable de DRF (par ex.
    # le lien "Log in" sur http://localhost:8000/users/). Utile uniquement
    # dans le navigateur — les vrais clients API doivent utiliser /login (JWT).
    path("api-auth/", include("rest_framework.urls",
        namespace="rest_framework")),
]
