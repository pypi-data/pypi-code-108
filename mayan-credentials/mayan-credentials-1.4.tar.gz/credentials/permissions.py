from django.utils.translation import ugettext_lazy as _

from mayan.apps.permissions import PermissionNamespace

namespace = PermissionNamespace(label=_('Credentials'), name='credentials')

permission_credential_create = namespace.add_permission(
    label=_('Create credentials'), name='credential_create'
)
permission_credential_delete = namespace.add_permission(
    label=_('Delete credentials'), name='credential_delete'
)
permission_credential_edit = namespace.add_permission(
    label=_('Edit credentials'), name='credential_edit'
)
permission_credential_use = namespace.add_permission(
    label=_('Use credential'), name='credential_use'
)
permission_credential_view = namespace.add_permission(
    label=_('View credentials'), name='credential_view'
)
