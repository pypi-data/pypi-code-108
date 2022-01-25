from django.utils.translation import ugettext_lazy as _

from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(label=_('Importer'), name='importer')

event_import_setup_created = namespace.add_event_type(
    label=_('Import setup created'), name='import_setup_created'
)
event_import_setup_edited = namespace.add_event_type(
    label=_('Import setup edited'), name='import_setup_edited'
)
event_import_setup_item_completed = namespace.add_event_type(
    label=_('Import setup item completed'), name='import_setup_item_completed'
)
event_import_setup_process_ended = namespace.add_event_type(
    label=_('Import setup process ended'), name='import_setup_process_ended'
)
event_import_setup_process_started = namespace.add_event_type(
    label=_('Import setup process started'),
    name='import_setup_process_started'
)
event_import_setup_populate_ended = namespace.add_event_type(
    label=_('Import setup populate ended'), name='import_setup_populate_ended'
)
event_import_setup_populate_started = namespace.add_event_type(
    label=_('Import setup populate started'),
    name='import_setup_populate_started'
)
