from rest_framework.permissions import BasePermission

# One permission class per CRUD action on UserViewSet (see get_permissions()
# in views.py), each checking a single Django model permission via
# request.user.has_perm(). Superusers pass every has_perm() check
# automatically regardless of assigned permissions/groups.


class CanCreateUser(BasePermission):  # create
    def has_permission(self, request, view):
        return request.user.has_perm("users.add_user")


class CanListUsers(BasePermission):  # read liste
    def has_permission(self, request, view):
        return request.user.has_perm("users.view_user")


class CanRetrieveUser(BasePermission):  # read detail
    def has_permission(self, request, view):
        return request.user.has_perm("users.view_user")


class CanUpdateUser(BasePermission):  # update complet
    # BUG: "update_user" is not one of Django's default model permissions
    # (add/change/delete/view). Unless a custom permission with this exact
    # codename is added to User.Meta.permissions, has_perm() always returns
    # False here — update/partial_update are effectively always 403, even
    # for staff. Not fixed; noting it so it isn't mistaken for "not yet
    # implemented" if a QA pass turns it up again.
    def has_permission(self, request, view):
        return request.user.has_perm("users.update_user")


class CanPartialUpdateUser(BasePermission):  # update partiel
    # Same "update_user" issue as CanUpdateUser above.
    def has_permission(self, request, view):
        return request.user.has_perm("users.update_user")


class CanDeleteUser(BasePermission):  # delete
    def has_permission(self, request, view):
        return request.user.has_perm("users.delete_user")
