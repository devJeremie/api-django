# Crée les trois lignes auth.Group dont UserViewSet.create() (views.py)
# a besoin — elle en recherche une par son nom ("admin"/"moderator"/"user",
# correspondant à User.role) et y attache le nouvel utilisateur. Sans cette
# migration, POST /users/ échoue avec Group.DoesNotExist quel que soit le
# rôle demandé. S'exécute automatiquement lors du `migrate`, en Docker et en local.
from django.db import migrations


def create_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in ("admin", "moderator", "user"):
        Group.objects.get_or_create(name=name)


def delete_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Group.objects.filter(name__in=("admin", "moderator", "user")).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        # reverse_code (delete_groups) permet de désappliquer proprement
        # cette migration avec `migrate users 0001` si jamais nécessaire.
        migrations.RunPython(create_groups, delete_groups),
    ]
