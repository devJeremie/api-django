from rest_framework.permissions import BasePermission

class CanCreateUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("users.add_user")

class CanListUsers(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("users.view_user")

class CanRetrieveUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("users.view_user")

class CanUpdateUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("users.update_user")

class CanPartialUpdateUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("users.update_user")

class CanDeleteUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("users.delete_user")