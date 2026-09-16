# Seeds the three auth.Group rows that UserViewSet.create() (views.py)
# expects to exist — it looks one up by name ("admin"/"moderator"/"user",
# matching User.role) and attaches the new user to it. Without this
# migration, POST /users/ fails with Group.DoesNotExist regardless of the
# role requested. Runs automatically on `migrate`, in Docker and locally.
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
        # reverse_code (delete_groups) makes this migration unappliable
        # cleanly with `migrate users 0001` if ever needed.
        migrations.RunPython(create_groups, delete_groups),
    ]
