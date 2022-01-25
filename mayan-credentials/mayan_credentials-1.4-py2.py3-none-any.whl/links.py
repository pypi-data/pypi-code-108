from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link
from mayan.apps.navigation.utils import factory_condition_queryset_access

from .icons import (
    icon_stored_credential_backend_selection,
    icon_stored_credential_delete, icon_stored_credential_edit,
    icon_stored_credential_list, icon_stored_credential_setup
)
from .permissions import (
    permission_credential_create, permission_credential_delete,
    permission_credential_edit, permission_credential_view
)

link_stored_credential_backend_selection = Link(
    icon=icon_stored_credential_backend_selection,
    permissions=(permission_credential_create,),
    text=_('Create credential'),
    view='credentials:stored_credential_backend_selection',
)
link_stored_credential_delete = Link(
    args='resolved_object.pk',
    icon=icon_stored_credential_delete,
    permissions=(permission_credential_delete,),
    tags='dangerous', text=_('Delete'),
    view='credentials:stored_credential_delete',
)
link_stored_credential_edit = Link(
    args='object.pk',
    icon=icon_stored_credential_edit,
    permissions=(permission_credential_edit,),
    text=_('Edit'), view='credentials:stored_credential_edit',
)
link_stored_credential_list = Link(
    icon=icon_stored_credential_list,
    permissions=(permission_credential_view,),
    text=_('Credential list'), view='credentials:stored_credential_list',
)
link_stored_credential_setup = Link(
    condition=factory_condition_queryset_access(
        app_label='credentials', model_name='StoredCredential',
        object_permission=permission_credential_view,
        view_permission=permission_credential_create,
    ), icon=icon_stored_credential_setup,
    text=_('Credentials'),
    view='credentials:stored_credential_list'
)
