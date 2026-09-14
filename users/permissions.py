from rest_framework.permissions import BasePermission

# Differentes actions du crud
class CanCreateUser(BasePermission): #create
    def has_permission(self, request, view):
        return request.user.has_perm("users.add_user")

class CanListUsers(BasePermission): #read liste
    def has_permission(self, request, view):
        return request.user.has_perm("users.view_user")

class CanRetrieveUser(BasePermission): #read detail
    def has_permission(self, request, view):
        return request.user.has_perm("users.view_user")

class CanUpdateUser(BasePermission):  #update complet
    def has_permission(self, request, view):
        return request.user.has_perm("users.update_user")

class CanPartialUpdateUser(BasePermission):  #update partiel
    def has_permission(self, request, view):
        return request.user.has_perm("users.update_user")

class CanDeleteUser(BasePermission):  #delete
    def has_permission(self, request, view):
        return request.user.has_perm("users.delete_user")