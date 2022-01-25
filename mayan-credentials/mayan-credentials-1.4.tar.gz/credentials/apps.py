import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import menu_object, menu_secondary, menu_setup
from mayan.apps.events.classes import EventModelRegistry, ModelEventType
from mayan.apps.navigation.classes import SourceColumn

from .classes import CredentialBackend
from .events import event_credential_edited, event_credential_used
from .links import (
    link_stored_credential_backend_selection, link_stored_credential_delete,
    link_stored_credential_edit, link_stored_credential_list,
    link_stored_credential_setup
)
from .permissions import (
    permission_credential_delete, permission_credential_edit,
    permission_credential_use, permission_credential_view
)

logger = logging.getLogger(name=__name__)


class CredentialsApp(MayanAppConfig):
    app_namespace = 'credentials'
    app_url = 'credentials'
    has_rest_api = True
    has_tests = True
    name = 'credentials'
    verbose_name = _('Credentials')

    def ready(self):
        super().ready()

        CredentialBackend.load_modules()

        StoredCredential = self.get_model(model_name='StoredCredential')

        EventModelRegistry.register(model=StoredCredential)

        ModelEventType.register(
            model=StoredCredential, event_types=(
                event_credential_edited, event_credential_used
            )
        )

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=StoredCredential
        )
        SourceColumn(
            attribute='internal_name', include_label=True, is_sortable=True,
            source=StoredCredential
        )
        SourceColumn(
            attribute='get_backend_label', include_label=True,
            source=StoredCredential
        )

        ModelPermission.register(
            model=StoredCredential, permissions=(
                permission_credential_delete, permission_credential_edit,
                permission_credential_view, permission_credential_use
            )
        )

        menu_object.bind_links(
            links=(
                link_stored_credential_delete, link_stored_credential_edit
            ), sources=(StoredCredential,)
        )

        menu_secondary.bind_links(
            links=(
                link_stored_credential_list,
                link_stored_credential_backend_selection
            ), sources=(
                StoredCredential,
                'credentials:stored_credential_backend_selection',
                'credentials:stored_credential_create',
                'credentials:stored_credential_list'
            )
        )

        menu_setup.bind_links(
            links=(link_stored_credential_setup,)
        )
