import json

from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
from django.db import models
from django.db.models import Max
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import ugettext_lazy as _

from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.tasks import task_document_file_upload
from mayan.apps.events.classes import (
    EventManagerMethodAfter, EventManagerSave
)
from mayan.apps.events.decorators import method_event

from credentials.models import StoredCredential

from .classes import NullBackend
from .events import (
    event_import_setup_created, event_import_setup_edited,
    event_import_setup_populate_ended, event_import_setup_populate_started,
    event_import_setup_process_ended, event_import_setup_process_started,
    event_import_setup_item_completed
)
from .literals import (
    DEFAULT_PROCESS_SIZE, ITEM_STATE_CHOICES, ITEM_STATE_COMPLETE,
    ITEM_STATE_DOWNLOADED, ITEM_STATE_ERROR, ITEM_STATE_NONE,
    SETUP_STATE_CHOICES, SETUP_STATE_ERROR, SETUP_STATE_EXECUTING,
    SETUP_STATE_NONE, SETUP_STATE_POPULATING
)
from .tasks import task_import_setup_item_process

ENABLE_STATE_CHANGE = False
IMPORT_ERROR_EXCLUSION_TEXTS = (
    'doesn\'t look like a module path'
)


class BackendModelMixin(models.Model):
    # TODO: Use common.model_mixins.BackendModelMixin after upgrade to
    # version 4.0.
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
        abstract = True

    def get_backend(self):
        """
        Retrieves the backend by importing the module and the class.
        """
        try:
            return import_string(dotted_path=self.backend_path)
        except ImportError as exception:
            for import_error_exclusion_text in IMPORT_ERROR_EXCLUSION_TEXTS:
                if import_error_exclusion_text in str(exception):
                    raise
            return NullBackend

    def get_backend_instance(self):
        return self.get_backend()(**self.get_backend_data())

    def get_backend_label(self):
        """
        Return the label that the backend itself provides. The backend is
        loaded but not initialized. As such the label returned is a class
        property.
        """
        try:
            return self.get_backend().label
        except ImportError:
            return _('Unknown backend')

    get_backend_label.short_description = _('Backend')
    get_backend_label.help_text = _('The backend class for this entry.')

    def get_backend_data(self):
        return json.loads(s=self.backend_data or '{}')

    def set_backend_data(self, obj):
        self.backend_data = json.dumps(obj=obj)


class ImportSetup(BackendModelMixin, models.Model):
    label = models.CharField(
        help_text=_('Short description of this import setup.'), max_length=128,
        unique=True, verbose_name=_('Label')
    )
    credential = models.ForeignKey(
        blank=True, null=True, on_delete=models.CASCADE,
        related_name='import_setups', to=StoredCredential,
        verbose_name=_('Credential')
    )
    document_type = models.ForeignKey(
        on_delete=models.CASCADE, related_name='import_setups',
        to=DocumentType, verbose_name=_('Document type')
    )
    process_size = models.PositiveIntegerField(
        default=DEFAULT_PROCESS_SIZE, help_text=_(
            'Number of items to process per execution.'
        ), verbose_name=_('Process size')
    )
    state = models.PositiveIntegerField(
        choices=SETUP_STATE_CHOICES, default=SETUP_STATE_NONE, help_text=_(
            'The last recorded state of the import setup.'
        ), verbose_name=_('State')
    )

    class Meta:
        ordering = ('label',)
        verbose_name = _('Import setup')
        verbose_name_plural = _('Import setups')

    def __str__(self):
        return self.label

    def clear(self):
        self.items.all().delete()

    def get_backend_instance(self):
        kwargs = self.get_backend_data()

        if self.credential:
            kwargs.update(
                {
                    'credential_class': self.credential.get_backend(),
                    'credential_data': self.credential.get_backend_data()
                }
            )

        return self.get_backend()(**kwargs)

    def get_state_label(self):
        return self.get_state_display()
    get_state_label.short_description = _('State')
    get_state_label.help_text = _(
        'The last recorded state of the setup item. The field will be '
        'sorted by the numeric value of the state and not the actual text.'
    )

    def item_count_all(self):
        return self.items.count()

    item_count_all.short_description = _('Items')

    def item_count_complete(self):
        return self.items.filter(state=ITEM_STATE_COMPLETE).count()

    item_count_complete.short_description = _('Items complete')

    def item_count_percent(self):
        items_complete = self.item_count_complete()
        items_all = self.item_count_all()

        if items_all == 0:
            percent = 0
        else:
            percent = items_complete / items_all * 100.0

        return '{} of {} ({:.0f}%)'.format(
            intcomma(value=items_complete), intcomma(value=items_all),
            percent
        )

    item_count_percent.short_description = _('Progress')

    def populate(self, user=None):
        event_import_setup_populate_started.commit(
            actor=user, target=self
        )

        if ENABLE_STATE_CHANGE:
            self.state = SETUP_STATE_POPULATING
            self.save()

        try:
            backend = self.get_backend_instance()

            for item in backend.get_item_list():

                identifer_field = backend.item_identifier
                try:
                    # Try as an attribute
                    identifier = getattr(item, identifer_field)
                except (AttributeError, TypeError):
                    # Try as dictionary
                    identifier = item[identifer_field]

                setup_item, created = self.items.get_or_create(
                    identifier=identifier
                )
                if created:
                    setup_item.dump_data(
                        obj=item
                    )
                    setup_item.save()
        except Exception as exception:
            if ENABLE_STATE_CHANGE:
                self.state = SETUP_STATE_ERROR
                self.save()

            self.logs.create(
                text=str(exception)
            )

            if settings.DEBUG:
                raise
        else:
            if ENABLE_STATE_CHANGE:
                self.state = SETUP_STATE_NONE
                self.save()

            event_import_setup_populate_ended.commit(
                actor=user, target=self
            )

            self.logs.all().delete()

    def process(self, user=None):
        """
        Iterate of the ImportSetupItem instances downloading and creating
        documents from them.
        """
        if ENABLE_STATE_CHANGE:
            self.state = SETUP_STATE_EXECUTING
            self.save()

        event_import_setup_process_started.commit(
            actor=user, target=self
        )

        count = 0
        try:
            queryset = self.items.filter(state=ITEM_STATE_NONE)
            iterator = queryset.iterator()

            while True:
                item = next(iterator)
                if item.check_valid():
                    count = count + 1
                    task_import_setup_item_process.apply_async(
                        kwargs={
                            'import_setup_item_id': item.pk
                        }
                    )
                    if count >= self.process_size:
                        break
        except StopIteration:
            """
            Expected exception when iterator is exhausted before the process
            size is reached.
            """
        except Exception as exception:
            if ENABLE_STATE_CHANGE:
                self.state = SETUP_STATE_ERROR
                self.save()

            self.logs.create(
                text=str(exception)
            )

            if settings.DEBUG:
                raise

            # Exit the method to avoid committing the ended event.
            return

        # This line is reached on StopIteration or from the break in the loop.
        if ENABLE_STATE_CHANGE:
            self.state = SETUP_STATE_NONE
            self.save()

        self.logs.all().delete()

        event_import_setup_process_ended.commit(
            actor=user, target=self
        )

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_import_setup_created,
            'target': 'self',
        },
        edited={
            'event': event_import_setup_edited,
            'target': 'self',
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)


class ImportSetupAction(BackendModelMixin, models.Model):
    import_setup = models.ForeignKey(
        on_delete=models.CASCADE, related_name='actions', to=ImportSetup,
        verbose_name=_('Import Setup')
    )
    label = models.CharField(
        max_length=255, help_text=_('A short text describing the action.'),
        verbose_name=_('Label')
    )
    enabled = models.BooleanField(default=True, verbose_name=_('Enabled'))
    order = models.PositiveIntegerField(
        blank=True, db_index=True, default=0, help_text=_(
            'Order in which the action will be executed. If left '
            'unchanged, an automatic order value will be assigned.'
        ), verbose_name=_('Order')
    )

    class Meta:
        ordering = ('order', 'label')
        unique_together = (
            ('import_setup', 'order'), ('import_setup', 'label')
        )
        verbose_name = _('Import setup action')
        verbose_name_plural = _('Import setup actions')

    def __str__(self):
        return self.label

    def execute(self, context=None):
        if not context:
            context = {}

        return self.get_backend_instance().execute(context=context)

    def get_next_order(self):
        last_order = self.import_setup.actions.aggregate(
            Max('order')
        )['order__max']

        if last_order is not None:
            return last_order + 1
        else:
            return 0

    def save(self, *args, **kwargs):
        if not self.order:
            self.order = self.get_next_order()
        super().save(*args, **kwargs)


class ImportSetupItem(models.Model):
    import_setup = models.ForeignKey(
        on_delete=models.CASCADE, related_name='items',
        to=ImportSetup, verbose_name=_('Import setup')
    )
    identifier = models.CharField(
        db_index=True, max_length=64, verbose_name=_('Identifier')
    )
    serialized_data = models.TextField(
        blank=True, default='{}', verbose_name=_('Serialized data')
    )
    state = models.IntegerField(
        db_index=True, choices=ITEM_STATE_CHOICES, default=ITEM_STATE_NONE,
        verbose_name=_('State')
    )
    state_data = models.TextField(blank=True, verbose_name=_('State data'))
    documents = models.ManyToManyField(
        blank=True, related_name='import_items',
        to=Document, verbose_name=_('Document')
    )

    class Meta:
        verbose_name = _('Import setup item')
        verbose_name_plural = _('Import setup items')

    def __str__(self):
        return self.identifier

    def check_valid(self):
        backend_instance = self.import_setup.get_backend_instance()
        return backend_instance.check_valid(
            identifier=self.identifier, data=self.data
        )

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_import_setup_item_completed,
        action_object='import_setup',
        target='self',
    )
    def create_document(self, shared_uploaded_file):
        """
        Create a document from a downloaded ImportSetupItem instance.
        """
        backend_class = self.import_setup.get_backend()
        document_type = self.import_setup.document_type
        label = self.data.get(backend_class.item_label, self.id)

        try:
            document = Document.objects.create(
                document_type=document_type, label=label
            )
        except Exception as exception:
            self.state = ITEM_STATE_ERROR
            self.state_data = str(exception)
            self.save()
            if settings.DEBUG:
                raise
        else:
            self.state = ITEM_STATE_COMPLETE
            self.state_data = ''
            self.save()

            task_document_file_upload.apply_async(
                kwargs={
                    'document_id': document.pk,
                    'filename': document.label,
                    'shared_uploaded_file_id': shared_uploaded_file.pk,
                }
            )

            return document

    @cached_property
    def data(self):
        return self.load_data()

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_import_setup_edited,
        action_object='self',
        target='import_setup',
    )
    def delete(self):
        return super().delete()

    def load_data(self):
        return json.loads(s=self.serialized_data)

    def get_data_display(self):
        return ', '.join(
            [
                '"{}": "{}"'.format(key, value) for key, value in self.data.items()
            ]
        )
    get_data_display.short_description = _('Data')

    def dump_data(self, obj):
        self.serialized_data = json.dumps(obj=obj)

    def get_state_label(self):
        return self.get_state_display()
    get_state_label.help_text = _(
        'The last recorded state of the item. The field will be sorted by '
        'the numeric value of the state and not the actual text.'
    )
    get_state_label.short_description = _('State')

    def process(self):
        shared_uploaded_file = None

        if self.state == ITEM_STATE_NONE:
            try:
                backend_instance = self.import_setup.get_backend_instance()
                shared_uploaded_file = backend_instance.item_process(
                    identifier=self.identifier, data=self.data
                )
            except Exception as exception:
                self.state = ITEM_STATE_ERROR
                self.state_data = str(exception)
                self.save()
                if settings.DEBUG:
                    raise
            else:
                self.state = ITEM_STATE_DOWNLOADED
                self.state_data = ''
                self.save()

            if shared_uploaded_file:
                document = self.create_document(
                    shared_uploaded_file=shared_uploaded_file
                )
                if document:
                    self.documents.add(document)

                    context = {'document': document, 'self': self}
                    for action in self.import_setup.actions.filter(enabled=True):
                        action.execute(context=context)


class ImportSetupLog(models.Model):
    import_setup = models.ForeignKey(
        on_delete=models.CASCADE, related_name='logs',
        to=ImportSetup, verbose_name=_('Import setup log')
    )
    datetime = models.DateTimeField(
        auto_now_add=True, db_index=True, editable=False,
        verbose_name=_('Date time')
    )
    text = models.TextField(
        blank=True, editable=False, verbose_name=_('Text')
    )

    class Meta:
        get_latest_by = 'datetime'
        ordering = ('-datetime',)
        verbose_name = _('Log entry')
        verbose_name_plural = _('Log entries')
