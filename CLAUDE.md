# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

The virtualenv lives in `env/` at the project root (Windows). Activate it before running anything:

```powershell
env\Scripts\Activate.ps1      # PowerShell
# or: env\Scripts\activate.bat
```

There is no `requirements.txt`/`pyproject.toml` — dependencies are installed directly into `env/`. Currently installed: Django 5.1.15, djangorestframework 3.18.1, djangorestframework-simplejwt 5.5.1, drf-spectacular 0.30.0, mysqlclient 2.2.8 (Python 3.13). If `env/` is missing or out of date, reinstall with:

```powershell
pip install django djangorestframework djangorestframework-simplejwt drf-spectacular mysqlclient
```

The DB is MySQL, not the default sqlite — see Database note below. A local MySQL server must be running before `runserver`/`migrate` will work.

Common commands (run from the project root, same level as `manage.py`):

```powershell
python manage.py runserver              # start the dev server (http://127.0.0.1:8000/)
python manage.py check                  # validate settings/URLs without running the server
python manage.py makemigrations         # create migrations after model changes
python manage.py migrate                # apply migrations
python manage.py createsuperuser        # create an admin/API auth user
python manage.py test                   # run the test suite
python manage.py test users             # run tests for a single app
python manage.py shell                  # interactive shell with app models loaded
```

## Architecture

Single Django project `api/` (settings, root URLconf, WSGI/ASGI) plus one app, `users/`, that exposes a DRF-based REST API. The user model is custom: `users.User(AbstractUser)` in `users/models.py` adds a `role` field (`admin` / `moderator` / `user`, default `user`). `AUTH_USER_MODEL = "users.User"` in `api/settings.py` points Django at it.

**URL layout** — `api/urls.py` is the root URLconf:
- `path('', include("users.urls"))` mounts the users app at the root.
- `api/schema/` (name `schema`) and `api/` (name `swagger-ui`) serve drf-spectacular's OpenAPI schema and Swagger UI — the UI is at `/api/`, not `/api/swagger-ui`.
- `login` / `refreshtoken` wire up `djangorestframework-simplejwt`'s `TokenObtainPairView`/`TokenRefreshView` directly (JWT issuing/refresh).

`users/urls.py` registers a DRF `DefaultRouter` with `UserViewSet` under the `users` prefix, **with an explicit `basename="user"`** — required because `UserViewSet` is a plain `viewsets.ViewSet` (see below), which has no `.queryset` attribute the router could otherwise use to infer the basename. It also includes `rest_framework.urls` at `/api-auth/` for the browsable API's session login/logout.

**Views** (`users/views.py`):
- `UserViewSet(viewsets.ViewSet)` implements `list`/`create`/`retrieve`/`update`/`partial_update`/`destroy` by hand (not a `ModelViewSet`), querying `User.objects` directly in each method. `get_permissions()` picks a different permission class per action from `users/permissions.py` (`CanCreateUser`, `CanListUsers`, `CanRetrieveUser`, `CanUpdateUser`, `CanPartialUpdateUser`, `CanDeleteUser`) — each just checks a Django model permission via `request.user.has_perm(...)`. `create()` also assigns the new user into a matching `Group` ("admin"/"moderator"/"user") based on `role`, so those three groups must already exist in the DB (e.g. created via `/admin/` or a data migration) or `create` will raise `Group.DoesNotExist`.
- `UserLoginView(views.APIView)` authenticates username/password and returns a token — but it is **not wired into any urlpatterns**, so it's currently dead code; JWT login actually goes through simplejwt's `TokenObtainPairView` at `/login`.
- Every action is documented with `@extend_schema(...)` from drf-spectacular for the OpenAPI schema.

**Permissions gotcha**: `CanUpdateUser`/`CanPartialUpdateUser` check `request.user.has_perm("users.update_user")`, but Django's built-in model permissions are `add_user`/`change_user`/`delete_user`/`view_user` — there's no default `update_user` permission. Unless a custom permission with that codename is added to `User.Meta.permissions`, update/partial_update will always be denied (403) even for staff/superusers, since `has_perm` looks for a permission that doesn't exist.

`REST_FRAMEWORK` in `api/settings.py`: global `DEFAULT_AUTHENTICATION_CLASSES` is JWT (`rest_framework_simplejwt.authentication.JWTAuthentication`), global `DEFAULT_PERMISSION_CLASSES` is `IsAuthenticated` (overridden per-action on `UserViewSet` as above), pagination is `PageNumberPagination` at 10/page, and `DEFAULT_SCHEMA_CLASS` is drf-spectacular's `AutoSchema`.

## Database

`DATABASES` in `api/settings.py` is MySQL (not the `startproject` default sqlite): db name `api-rest-django`, user `root`, no password, `127.0.0.1:3306`. The commented-out sqlite block above it is the original default, kept for reference. Create the `api-rest-django` schema in MySQL yourself before running `migrate`.

`DEBUG = True` and `SECRET_KEY` is the default dev key generated by `startproject` — this is a local dev setup only, not deployment-configured (no `ALLOWED_HOSTS`, no env-based settings).
