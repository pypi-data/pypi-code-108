from django.utils.translation import ugettext_lazy as _

from mayan.apps.events.classes import EventTypeNamespace

namespace = EventTypeNamespace(label=_('Credentials'), name='credentials')

event_credential_created = namespace.add_event_type(
    label=_('Credential created'), name='credential_created'
)
event_credential_edited = namespace.add_event_type(
    label=_('Credential edited'), name='credential_edited'
)
event_credential_used = namespace.add_event_type(
    label=_('Credential used'), name='credential_used'
)
