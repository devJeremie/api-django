from django.contrib.auth.models import AbstractUser
from django.db.models import CharField

class User(AbstractUser):
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