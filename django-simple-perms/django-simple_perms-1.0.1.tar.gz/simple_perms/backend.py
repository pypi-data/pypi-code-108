from .registry import get_app_logic
from .settings import SIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION


class PermissionBackend(object):

    def has_perm(self, user, perm, obj=None):
        try:
            app_label, perm_name = perm.split('.')
        except Exception:
            raise AttributeError("The given perm attribute \"%s\" hasn\'t the required format : "
                                 "\"app_label.permission_name\"" % perm)

        logic = get_app_logic(app_label)

        if logic:
            if hasattr(logic, perm_name):
                return getattr(logic, perm_name)(user, obj, perm)
            else:
                return logic.default_permission(user, obj, perm)

        return SIMPLE_PERMS_GLOBAL_DEFAULT_PERMISSION(user, obj, perm)

    def authenticate(self, *args):
        return None
