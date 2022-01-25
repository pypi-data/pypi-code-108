import logging

from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.classes import ModelPermission
from mayan.apps.common.apps import MayanAppConfig
from mayan.apps.common.menus import (
    menu_list_facet, menu_multi_item, menu_object, menu_secondary,
    menu_setup
)
from mayan.apps.events.classes import EventModelRegistry, ModelEventType
from mayan.apps.navigation.classes import SourceColumn
from mayan.apps.views.html_widgets import TwoStateWidget

from .classes import ImportSetupActionBackend, ImportSetupBackend, ModelFiler
from .events import (
    event_import_setup_edited, event_import_setup_process_ended,
    event_import_setup_process_started, event_import_setup_populate_ended,
    event_import_setup_populate_started, event_import_setup_item_completed
)
from .links import (
    link_import_setup_backend_selection, link_import_setup_delete,
    link_import_setup_clear, link_import_setup_edit,
    link_import_setup_item_multiple_delete,
    link_import_setup_item_document_list,
    link_import_setup_item_multiple_process, link_import_setup_items_list,
    link_import_setup_logs, link_import_setup_multiple_clear,
    link_import_setup_multiple_populate, link_import_setup_multiple_process,
    link_import_setup_populate, link_import_setup_process,
    link_import_setup_list, link_import_setup_setup, link_model_filer_load,
    link_model_filer_save
)
from .links import (
    link_import_setup_action_backend_selection,
    link_import_setup_action_delete, link_import_setup_action_edit,
    link_import_setup_action_list
)
from .permissions import (
    permission_import_setup_delete, permission_import_setup_edit,
    permission_import_setup_process, permission_import_setup_view,
    permission_model_filer_load, permission_model_filer_save
)

logger = logging.getLogger(name=__name__)


class ImporterApp(MayanAppConfig):
    app_namespace = 'importer'
    app_url = 'importer'
    has_rest_api = True
    has_tests = True
    name = 'importer'
    verbose_name = _('Importer')

    def ready(self):
        super().ready()

        ImportSetupActionBackend.load_modules()
        ImportSetupBackend.load_modules()

        ImportSetup = self.get_model(model_name='ImportSetup')
        ImportSetupAction = self.get_model(model_name='ImportSetupAction')
        ImportSetupItem = self.get_model(model_name='ImportSetupItem')
        ImportSetupLog = self.get_model(model_name='ImportSetupLog')

        EventModelRegistry.register(model=ImportSetup)
        EventModelRegistry.register(model=ImportSetupItem)

        ModelEventType.register(
            model=ImportSetup, event_types=(
                event_import_setup_edited, event_import_setup_populate_ended,
                event_import_setup_populate_started,
                event_import_setup_process_ended,
                event_import_setup_process_started
            )
        )
        ModelEventType.register(
            model=ImportSetupItem, event_types=(
                event_import_setup_item_completed,
            )
        )

        ModelFiler(bulk_size=250, model=ImportSetupItem)

        ModelPermission.register(
            model=ImportSetup, permissions=(
                permission_import_setup_delete, permission_import_setup_edit,
                permission_import_setup_process,
                permission_import_setup_view, permission_model_filer_load,
                permission_model_filer_save
            )
        )

        ModelPermission.register_inheritance(
            model=ImportSetupAction, related='import_setup',
        )
        ModelPermission.register_inheritance(
            model=ImportSetupItem, related='import_setup',
        )

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=ImportSetup
        )
        SourceColumn(
            attribute='get_backend_label', include_label=True,
            source=ImportSetup
        )
        SourceColumn(
            attribute='item_count_percent', empty_value=_('0%'),
            include_label=True, source=ImportSetup
        )
        SourceColumn(
            attribute='get_state_label', include_label=True,
            is_sortable=True, sort_field='state', source=ImportSetup
        )

        SourceColumn(
            attribute='datetime', is_sortable=True, is_identifier=True,
            source=ImportSetupLog
        )
        SourceColumn(
            attribute='text', source=ImportSetupLog,
        )

        # Import Setup Action

        SourceColumn(
            attribute='label', is_identifier=True, is_sortable=True,
            source=ImportSetupAction
        )
        SourceColumn(
            attribute='enabled', include_label=True, is_sortable=True,
            source=ImportSetupAction, widget=TwoStateWidget
        )
        SourceColumn(
            attribute='order', include_label=True, is_sortable=True,
            source=ImportSetupAction
        )
        SourceColumn(
            attribute='get_backend_label', include_label=True,
            label=_('Action type'), source=ImportSetupAction
        )

        # Import Setup Item

        SourceColumn(
            attribute='identifier', is_identifier=True, is_sortable=True,
            source=ImportSetupItem
        )
        SourceColumn(
            attribute='get_data_display', source=ImportSetupItem
        )
        SourceColumn(
            attribute='get_state_label', is_sortable=True,
            sort_field='state', source=ImportSetupItem
        )
        SourceColumn(
            attribute='state_data', source=ImportSetupItem
        )

        # ImportSetup

        menu_list_facet.bind_links(
            links=(
                link_import_setup_items_list, link_import_setup_logs
            ), sources=(ImportSetup,)
        )

        menu_multi_item.bind_links(
            links=(
                link_import_setup_multiple_clear,
                link_import_setup_multiple_populate,
                link_import_setup_multiple_process
            ), sources=(ImportSetup,)
        )
        menu_object.bind_links(
            links=(
                link_import_setup_delete, link_import_setup_edit,
                link_import_setup_process, link_import_setup_clear,
                link_import_setup_populate,
                link_model_filer_load, link_model_filer_save
            ), sources=(ImportSetup,)
        )
        menu_secondary.bind_links(
            links=(
                link_import_setup_backend_selection, link_import_setup_list
            ),
            sources=(
                ImportSetup, 'importer:import_setup_backend_selection',
                'importer:import_setup_create', 'importer:import_setup_list'
            )
        )
        menu_setup.bind_links(
            links=(link_import_setup_setup,)
        )

        # Import setup action

        menu_list_facet.bind_links(
            links=(
                link_import_setup_action_list,
            ), sources=(ImportSetup,)
        )

        menu_object.bind_links(
            links=(
                link_import_setup_action_delete,
                link_import_setup_action_edit,
            ), sources=(ImportSetupAction,)
        )
        menu_secondary.bind_links(
            links=(
                link_import_setup_action_backend_selection,
            ), sources=(
                ImportSetup,
            )
        )

        # Import setup item

        menu_list_facet.bind_links(
            links=(
                link_import_setup_item_document_list,
            ), sources=(ImportSetupItem,)
        )
        menu_multi_item.bind_links(
            links=(
                link_import_setup_item_multiple_delete,
                link_import_setup_item_multiple_process
            ), sources=(ImportSetupItem,)
        )
