from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        """
        Allows access only to authenticated users with uid.
        """
        return bool(request.user and 'uid' in request.user.keys())


class IsLoggedInAndOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        kwargs = request.parser_context['kwargs']
        user_id = get_user_id(kwargs)
        return request.user and 'user_id' in request.user and user_id == request.user['user_id']


class IsLoggedInAndDoctor(permissions.BasePermission):
    def has_permission(self, request, view):
        kwargs = request.parser_context['kwargs']
        user_id = get_user_id(kwargs)

        return request.user and 'user_id' in request.user \
            and user_id == request.user['user_id']\
            and 'role' in request.user \
            and 'doctor' == request.user['role']


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and 'is_admin' in request.user and bool(request.user['is_admin'])


class IsAdminOrLoggedInAndOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user and 'is_admin' in request.user and bool(request.user['is_admin']):
            return True

        kwargs = request.parser_context['kwargs']
        user_id = get_user_id(kwargs)
        return request.user and 'user_id' in request.user and user_id == request.user['user_id']


def get_user_id(kwargs):
    user_id = None
    user_id = str(kwargs['user_id']) if 'user_id' in kwargs else user_id
    user_id = str(kwargs['id']) if 'id' in kwargs else user_id
    return user_id


class IsCustomUserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        for name in view.custom_permissions:
            try:
                if name == request.user['name']:
                    return True
            except (KeyError, TypeError):
                return False
        return False
