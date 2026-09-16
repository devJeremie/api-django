from django.urls import include, path
from rest_framework import routers

from users import views

router = routers.DefaultRouter()

# basename is required here: DefaultRouter normally infers it from
# viewset.queryset.model, but UserViewSet is a plain ViewSet (no .queryset
# attribute) since it queries User.objects by hand in each method — router
# registration fails with an AssertionError without this.
router.register(r"users", views.UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),

    # Session login/logout for the DRF browsable API (e.g. the "Log in" link
    # on http://localhost:8000/users/). Only useful in the browser — real API
    # clients should use /login (JWT) instead.
    path("api-auth/", include("rest_framework.urls",
        namespace="rest_framework")),
]
