from django.contrib.auth.models import AbstractUser
from django.db.models import CharField


class User(AbstractUser):
    """Custom user model (AUTH_USER_MODEL = "users.User" in settings).

    Adds a `role` field used purely as an app-level label — it drives which
    auth.Group (admin/moderator/user, see migration 0002) a user is added to
    on creation in UserViewSet.create(), and sets is_staff/is_superuser
    accordingly. It has no bearing on Django's built-in permission checks by
    itself; permissions.py checks concrete model permissions
    (add_user/view_user/...) via has_perm(), not this field.
    """

    ADMIN = "admin"
    MODERATOR = "moderator"
    USER = "user"

    ROLE_CHOICES = (
        (ADMIN, "Administrateur"),
        (MODERATOR, "Modérateur"),
        (USER, "Utilisateur"),
    )

    role = CharField(
        max_length=30, choices=ROLE_CHOICES, verbose_name="Rôle", default=USER
    )

    def __str__(self):
        return self.username + " - " + self.email + " - " + self.role
