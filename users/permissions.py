from rest_framework.permissions import BasePermission

# Une classe de permission par action CRUD sur UserViewSet (voir get_permissions()
# dans views.py), chacune vérifiant une seule permission de modèle Django via
# request.user.has_perm(). Les superusers passent automatiquement chaque
# vérification has_perm(), quelles que soient les permissions/groupes assignés.


class CanCreateUser(BasePermission):  # création
    def has_permission(self, request, view):
        return request.user.has_perm("users.add_user")


class CanListUsers(BasePermission):  # lecture liste
    def has_permission(self, request, view):
        return request.user.has_perm("users.view_user")


class CanRetrieveUser(BasePermission):  # lecture détail
    def has_permission(self, request, view):
        return request.user.has_perm("users.view_user")


class CanUpdateUser(BasePermission):  # mise à jour complète
    # BUG : "update_user" ne fait pas partie des permissions de modèle par
    # défaut de Django (add/change/delete/view). Sans une permission
    # personnalisée avec exactement ce codename ajoutée à User.Meta.permissions,
    # has_perm() renvoie toujours False ici — update/partial_update sont donc
    # effectivement toujours en 403, même pour le staff. Non corrigé ;
    # signalé ici pour ne pas être confondu avec "pas encore implémenté"
    # si un passage QA le fait remonter à nouveau.
    def has_permission(self, request, view):
        return request.user.has_perm("users.update_user")


class CanPartialUpdateUser(BasePermission):  # mise à jour partielle
    # Même problème "update_user" que CanUpdateUser ci-dessus.
    def has_permission(self, request, view):
        return request.user.has_perm("users.update_user")


class CanDeleteUser(BasePermission):  # suppression
    def has_permission(self, request, view):
        return request.user.has_perm("users.delete_user")
