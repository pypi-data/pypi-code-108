import json

from django.db import models
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from mayan.apps.common.validators import validate_internal_name
from mayan.apps.events.classes import (
    EventManagerMethodAfter, EventManagerSave
)
from mayan.apps.events.decorators import method_event

from .classes import NullBackend
from .events import (
    event_credential_created, event_credential_edited, event_credential_used
)


class StoredCredential(models.Model):
    # TODO: Use common.model_mixins.BackendModelMixin after upgrade to version
    # 4.0.
    label = models.CharField(
        help_text=_('Short description of this credential.'), max_length=128,
        unique=True, verbose_name=_('Label')
    )
    internal_name = models.CharField(
        db_index=True, help_text=_(
            'This value will be used by other apps to reference this '
            'credential. Can only contain letters, numbers, and underscores.'
        ), max_length=255, unique=True, validators=[validate_internal_name],
        verbose_name=_('Internal name')
    )
    backend_path = models.CharField(
        max_length=128,
        help_text=_('The dotted Python path to the backend class.'),
        verbose_name=_('Backend path')
    )
    backend_data = models.TextField(
        blank=True, help_text=_('JSON encoded data for the backend class.'),
        verbose_name=_('Backend data')
    )

    class Meta:
        ordering = ('label',)
        verbose_name = _('Credential')
        verbose_name_plural = _('Credentials')

    def __str__(self):
        return self.label

    def get_backend(self):
        """
        Retrieves the backend by importing the module and the class.
        """
        try:
            return import_string(dotted_path=self.backend_path)
        except ImportError:
            return NullBackend

    def get_backend_label(self):
        """
        Return the label that the backend itself provides. The backend is
        loaded but not initialized. As such the label returned is a class
        property.
        """
        return self.get_backend().label

    get_backend_label.short_description = _('Backend')
    get_backend_label.help_text = _('The backend class for this entry.')

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_credential_used,
        target='self',
    )
    def get_backend_data(self):
        obj = json.loads(s=self.backend_data or '{}')
        backend = self.get_backend()
        if hasattr(backend, 'post_processing'):
            obj = backend.post_processing(obj=obj)

        return obj

    def set_backend_data(self, obj):
        self.backend_data = json.dumps(obj=obj)

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_credential_created,
            'target': 'self',
        },
        edited={
            'event': event_credential_edited,
            'target': 'self',
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
