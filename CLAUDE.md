# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Two ways to run this project

The project runs identically **in Docker** or **locally in a venv** — `api/settings.py` reads DB config from environment variables with the local defaults baked in, so neither mode needs extra setup to stay in sync with the other.

### Docker (recommended)

```powershell
docker-compose up -d              # start db (MySQL 8) + web (Django), builds the image if needed
docker-compose ps                 # check status — db should show "healthy"
docker-compose logs web --tail=20 # tail the dev server log
docker-compose down               # stop everything, keep the mysql_data volume (data survives)
docker-compose down -v            # stop AND wipe the MySQL volume (fresh DB next start)
```

Common one-offs (run inside the `web` container):

```powershell
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell
docker-compose run --rm web python manage.py migrate   # use `run --rm` instead of `exec` when containers aren't up yet
```

App: `http://localhost:8000/`. MySQL is reachable from the host on `localhost:3307` (not 3306 — see Database note). This machine's Docker install only has the legacy `docker-compose` (hyphenated) binary, not the `docker compose` plugin — use the hyphenated form.

**Files involved**: `Dockerfile` (Python 3.13-slim + build deps for `mysqlclient`, runs `manage.py runserver 0.0.0.0:8000`), `docker-compose.yml` (services `db` + `web`), `.dockerignore`, `.env` (real values, not committed) / `.env.example` (template, committed), `requirements.txt` (pinned deps, mirrors what's installed in `env/`).

### Local venv (without Docker)

The virtualenv lives in `env/` at the project root (Windows). Activate it before running anything:

```powershell
env\Scripts\Activate.ps1      # PowerShell
# or: env\Scripts\activate.bat
```

Dependencies are pinned in `requirements.txt` (Django 5.2.17, djangorestframework 3.18.1, djangorestframework-simplejwt 5.5.1, drf-spectacular 0.30.0, mysqlclient 2.2.8; Python 3.13). Reinstall with:

```powershell
pip install -r requirements.txt
```

Needs a MySQL server reachable at `127.0.0.1:3306` (the env-var defaults in `api/settings.py`) — a local MySQL install, separate from the one Docker runs (which is why Docker's MySQL is published on host port 3307, to avoid clashing with this one).

```powershell
python manage.py runserver              # http://127.0.0.1:8000/
python manage.py check                  # validate settings/URLs without running the server
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py test
python manage.py test users
python manage.py shell
```

**Keep `requirements.txt` and this venv in sync** — they drifted once already (venv had Django 5.1.15 installed with djangorestframework 3.18.1, which actually requires `django>=5.2`; `pip check` didn't catch it until a Docker build did a fresh dependency resolution). Run `pip check` after changing versions.

## Architecture

Single Django project `api/` (settings, root URLconf, WSGI/ASGI) plus one app, `users/`, that exposes a DRF-based REST API. The user model is custom: `users.User(AbstractUser)` in `users/models.py` adds a `role` field (`admin` / `moderator` / `user`, default `user`). `AUTH_USER_MODEL = "users.User"` in `api/settings.py` points Django at it.

**URL layout** — `api/urls.py` is the root URLconf:
- `path('', include("users.urls"))` mounts the users app at the root.
- `api/schema/` (name `schema`) and `api/` (name `swagger-ui`) serve drf-spectacular's OpenAPI schema and Swagger UI — the UI is at `/api/`, not `/api/swagger-ui`.
- `login` / `refreshtoken` wire up `djangorestframework-simplejwt`'s `TokenObtainPairView`/`TokenRefreshView` directly (JWT issuing/refresh).
- There is no `admin/` route (Django admin site) in the current `urlpatterns` — it was removed at some point; `/admin/` 404s, and that's expected, not a bug.

`users/urls.py` registers a DRF `DefaultRouter` with `UserViewSet` under the `users` prefix, **with an explicit `basename="user"`** — required because `UserViewSet` is a plain `viewsets.ViewSet` (see below), which has no `.queryset` attribute the router could otherwise use to infer the basename. It also includes `rest_framework.urls` at `/api-auth/` for the browsable API's session login/logout (`http://localhost:8000/users/` → "Log in" link in the top-right nav bar).

**Views** (`users/views.py`):
- `UserViewSet(viewsets.ViewSet)` implements `list`/`create`/`retrieve`/`update`/`partial_update`/`destroy` by hand (not a `ModelViewSet`), querying `User.objects` directly in each method — note `list()` builds the `Response` itself and does **not** go through DRF's pagination machinery, so `REST_FRAMEWORK["DEFAULT_PAGINATION_CLASS"]` has no effect on this endpoint despite being configured. `get_permissions()` picks a different permission class per action from `users/permissions.py` (`CanCreateUser`, `CanListUsers`, `CanRetrieveUser`, `CanUpdateUser`, `CanPartialUpdateUser`, `CanDeleteUser`) — each just checks a Django model permission via `request.user.has_perm(...)`.
- `create()` calls `validate_password()` **before** `user.save()` — a weak/common password raises Django's (not DRF's) `ValidationError`, which nothing catches, so it surfaces as an unhandled 500 instead of a clean 400. On success it assigns the new user into a matching `Group` ("admin"/"moderator"/"user") based on `role`, via `Group.objects.get(name=...)` **after** `user.save()` — so if the group lookup ever fails again (e.g. `0002_create_default_groups` migration not applied), the `User` row is still created even though the request returns 500. No `transaction.atomic()` around this method.
- `UserLoginView(views.APIView)` authenticates username/password and returns a token — but it is **not wired into any urlpatterns**, so it's currently dead code (predates the Docker work); JWT login actually goes through simplejwt's `TokenObtainPairView` at `/login`.
- Every action is documented with `@extend_schema(...)` from drf-spectacular for the OpenAPI schema.

**`users/migrations/0002_create_default_groups.py`** creates the `admin`/`moderator`/`user` `Group` rows via `RunPython` (reversible) — required for `UserViewSet.create()` to succeed at all, since it always looks up a `Group` matching the new user's `role`. Runs automatically on `migrate`, in both Docker and local mode.

**Permissions gotcha (still open, not fixed)**: `CanUpdateUser`/`CanPartialUpdateUser` check `request.user.has_perm("users.update_user")`, but Django's built-in model permissions are `add_user`/`change_user`/`delete_user`/`view_user` — there's no default `update_user` permission. Unless a custom permission with that codename is added to `User.Meta.permissions`, `update`/`partial_update` will always be denied (403) even for staff/superusers, since `has_perm` looks for a permission that doesn't exist.

`REST_FRAMEWORK` in `api/settings.py`: `DEFAULT_AUTHENTICATION_CLASSES` is `JWTAuthentication` **and** `SessionAuthentication` (the latter added so the `/api-auth/login/` session-login flow actually authenticates API requests — it didn't originally, since only JWT was listed and the session cookie was simply ignored by every view). `DEFAULT_PERMISSION_CLASSES` is `IsAuthenticated` (overridden per-action on `UserViewSet` as above). `DEFAULT_SCHEMA_CLASS` is drf-spectacular's `AutoSchema`.

## Database

`DATABASES` in `api/settings.py` is MySQL (not the `startproject` default sqlite, which is commented out just above for reference), configured via `os.environ.get(...)` for `NAME`/`USER`/`PASSWORD`/`HOST`/`PORT`, each defaulting to the original hardcoded local values (`api-rest-django` / `root` / *(empty)* / `127.0.0.1` / `3306`) — so local mode needs no `.env` at all, while Docker mode gets `db` / `3306` from `.env`'s `DB_HOST`/`DB_PORT`.

In Docker, MySQL's `root` account only accepts connections from `localhost` by default — the `web` container connecting from the Docker network was rejected (`Host '...' is not allowed to connect`) until `.env` set `MYSQL_ROOT_HOST=%`. That setting only takes effect at the **first** initialization of the data directory, so changing it after the fact requires `docker-compose down -v` (wipes `mysql_data`) before the next `up`.

The `db` service publishes MySQL on host port **3307**, not 3306 — a local MySQL install (used by local/non-Docker mode) already occupies 3306 on this machine, so Docker's MySQL was moved to avoid the conflict. Internally, `web` still talks to `db` on port 3306 (Docker's internal network is unaffected by the host port mapping).

`DEBUG = True` and `SECRET_KEY` is the default dev key generated by `startproject` — this is a local dev setup only, not deployment-configured (no `ALLOWED_HOSTS`, no env-based settings beyond the database ones above).
