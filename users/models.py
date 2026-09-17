from django.contrib.auth.models import AbstractUser
from django.db.models import CharField


class User(AbstractUser):
    """Modèle utilisateur personnalisé (AUTH_USER_MODEL = "users.User" dans settings).

    Ajoute un champ `role` utilisé purement comme étiquette au niveau de
    l'application — il détermine à quel auth.Group (admin/moderator/user,
    voir la migration 0002) un utilisateur est ajouté lors de sa création
    dans UserViewSet.create(), et définit is_staff/is_superuser en
    conséquence. Il n'a en soi aucune incidence sur les vérifications de
    permissions intégrées de Django ; permissions.py vérifie les permissions
    concrètes du modèle (add_user/view_user/...) via has_perm(), pas ce champ.
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
