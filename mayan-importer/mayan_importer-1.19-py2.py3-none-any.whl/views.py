import logging

from django.contrib import messages
from django.core.files import File
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.translation import ungettext, ugettext_lazy as _

from mayan.apps.documents.views.document_views import DocumentListView
from mayan.apps.storage.models import SharedUploadedFile
from mayan.apps.views.generics import (
    ConfirmView, FormView, MultipleObjectConfirmActionView,
    SingleObjectDeleteView, SingleObjectDynamicFormCreateView,
    SingleObjectDynamicFormEditView, SingleObjectDownloadView,
    SingleObjectListView
)
from mayan.apps.views.mixins import ExternalObjectViewMixin

from .classes import ImportSetupActionBackend, ImportSetupBackend, ModelFiler
from .forms import (
    ImportSetupActionSelectionForm, ImportSetupActionDynamicForm,
    ImportSetupBackendSelectionForm, ImportSetupBackendDynamicForm,
    ModelFilerUpload
)
from .icons import (
    icon_import_setup_action, icon_import_setup_items_list,
    icon_import_setup_list, icon_import_setup_log_list
)
from .links import (
    link_import_setup_action_backend_selection, link_import_setup_backend_selection,
    link_import_setup_populate
)
from .models import ImportSetup, ImportSetupAction, ImportSetupItem
from .permissions import (
    permission_import_setup_create, permission_import_setup_delete,
    permission_import_setup_edit, permission_import_setup_process,
    permission_import_setup_view, permission_model_filer_load,
    permission_model_filer_save
)
from .tasks import (
    task_import_setup_item_process, task_import_setup_process,
    task_import_setup_populate, task_model_filer_load, task_model_filer_save
)

logger = logging.getLogger(name=__name__)


class ImportSetupActionCreateView(
    ExternalObjectViewMixin, SingleObjectDynamicFormCreateView
):
    external_object_class = ImportSetup
    external_object_permission = permission_import_setup_edit
    external_object_pk_url_kwarg = 'import_setup_id'
    form_class = ImportSetupActionDynamicForm

    def get_class(self):
        try:
            return ImportSetupActionBackend.get(
                name=self.kwargs['class_path']
            )
        except KeyError:
            raise Http404(
                '{} class not found'.format(self.kwargs['class_path'])
            )

    def get_extra_context(self):
        return {
            'object': self.external_object,
            'title': _(
                'Create "%(import_setup_action)s" action for import '
                'setup: %(import_setup)s'
            ) % {
                'import_setup_action': self.get_class().label,
                'import_setup': self.external_object
            }
        }

    def get_form_extra_kwargs(self):
        return {
            'request': self.request,
            'backend_path': self.kwargs['class_path']
        }

    def get_form_schema(self):
        return self.get_class()().get_form_schema(
            request=self.request, import_setup=self.external_object
        )

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            'backend_path': self.kwargs['class_path'],
            'import_setup': self.external_object
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='importer:import_setup_action_list',
            kwargs={
                'import_setup_id': self.external_object.pk
            }
        )


class ImportSetupActionDeleteView(SingleObjectDeleteView):
    model = ImportSetupAction
    object_permission = permission_import_setup_edit
    pk_url_kwarg = 'import_setup_action_id'

    def get_extra_context(self):
        return {
            'navigation_object_list': (
                'import_setup', 'import_setup_action'
            ),
            'title': _('Delete import setup action: %s') % self.object,
            'import_setup': self.object.import_setup,
            'import_setup_action': self.object,
        }

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='importer:import_setup_action_list',
            kwargs={
                'import_setup_id': self.object.import_setup.pk
            }
        )


class ImportSetupActionEditView(SingleObjectDynamicFormEditView):
    form_class = ImportSetupActionDynamicForm
    model = ImportSetupAction
    object_permission = permission_import_setup_edit
    pk_url_kwarg = 'import_setup_action_id'

    def get_extra_context(self):
        return {
            'navigation_object_list': (
                'object', 'import_setup', 'import_setup_action'
            ),
            'title': _('Edit import setup state action: %s') % self.object,
            'import_setup': self.object.import_setup,
            'import_setup_action': self.object,
        }

    def get_form_extra_kwargs(self):
        return {
            'request': self.request,
            'backend_path': self.object.backend_path,
        }

    def get_form_schema(self):
        return self.object.get_backend_instance().get_form_schema(
            request=self.request, import_setup=self.object.import_setup
        )

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }

    def get_post_action_redirect(self):
        return reverse(
            viewname='importer:import_setup_action_list',
            kwargs={
                'import_setup_id': self.object.import_setup.pk
            }
        )


class ImportSetupActionListView(ExternalObjectViewMixin, SingleObjectListView):
    external_object_class = ImportSetup
    external_object_permission = permission_import_setup_view
    external_object_pk_url_kwarg = 'import_setup_id'

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_import_setup_action,
            'no_results_main_link': link_import_setup_action_backend_selection.resolve(
                context=RequestContext(
                    request=self.request, dict_={
                        'object': self.external_object
                    }
                )
            ),
            'no_results_text': _(
                'Import setup actions are macros that get executed when '
                'documents are imported.'
            ),
            'no_results_title': _(
                'There are no actions for this import setup.'
            ),
            'object': self.external_object,
            'title': _(
                'Actions for import setup: %s'
            ) % self.external_object,
        }

    def get_source_queryset(self):
        return self.external_object.actions.all()


class ImportSetupActionBackendSelectionView(ExternalObjectViewMixin, FormView):
    external_object_class = ImportSetup
    external_object_permission = permission_import_setup_edit
    external_object_pk_url_kwarg = 'import_setup_id'
    form_class = ImportSetupActionSelectionForm

    def get_extra_context(self):
        return {
            'object': self.external_object,
            'title': _(
                'New import setup action selection for: %s'
            ) % self.external_object,
        }

    def form_valid(self, form):
        class_path = form.cleaned_data['class_path']
        return HttpResponseRedirect(
            redirect_to=reverse(
                viewname='importer:import_setup_action_create',
                kwargs={
                    'import_setup_id': self.external_object.pk,
                    'class_path': class_path
                }
            )
        )


class ImportSetupBackendSelectionView(FormView):
    extra_context = {
        'title': _('New import backend selection'),
    }
    form_class = ImportSetupBackendSelectionForm
    view_permission = permission_import_setup_create

    def form_valid(self, form):
        backend = form.cleaned_data['backend']
        return HttpResponseRedirect(
            redirect_to=reverse(
                viewname='importer:import_setup_create', kwargs={
                    'class_path': backend
                }
            )
        )


class ImportSetupCreateView(SingleObjectDynamicFormCreateView):
    form_class = ImportSetupBackendDynamicForm
    post_action_redirect = reverse_lazy(
        viewname='importer:import_setup_list'
    )
    view_permission = permission_import_setup_create

    def get_backend(self):
        try:
            return ImportSetupBackend.get(name=self.kwargs['class_path'])
        except KeyError:
            raise Http404(
                '{} class not found'.format(self.kwargs['class_path'])
            )

    def get_extra_context(self):
        return {
            'title': _(
                'Create a "%s" import setup'
            ) % self.get_backend().label,
        }

    def get_form_schema(self):
        backend = self.get_backend()
        result = {
            'fields': backend.fields,
            'widgets': getattr(backend, 'widgets', {})
        }
        if hasattr(backend, 'field_order'):
            result['field_order'] = backend.field_order

        return result

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
            'backend_path': self.kwargs['class_path']
        }


class ImportSetupDeleteView(SingleObjectDeleteView):
    model = ImportSetup
    object_permission = permission_import_setup_delete
    pk_url_kwarg = 'import_setup_id'
    post_action_redirect = reverse_lazy(viewname='importer:import_setup_list')

    def get_extra_context(self):
        return {
            'import_setup': None,
            'object': self.object,
            'title': _('Delete the import setup: %s?') % self.object,
        }


class ImportSetupEditView(SingleObjectDynamicFormEditView):
    form_class = ImportSetupBackendDynamicForm
    model = ImportSetup
    object_permission = permission_import_setup_edit
    pk_url_kwarg = 'import_setup_id'
    post_action_redirect = reverse_lazy(viewname='importer:import_setup_list')

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit import setup: %s') % self.object,
        }

    def get_form_schema(self):
        backend = self.object.get_backend()
        result = {
            'fields': backend.fields,
            'widgets': getattr(backend, 'widgets', {})
        }
        if hasattr(backend, 'field_order'):
            result['field_order'] = backend.field_order

        return result

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }


class ImportSetupClearView(MultipleObjectConfirmActionView):
    model = ImportSetup
    object_permission = permission_import_setup_process
    pk_url_kwarg = 'import_setup_id'
    post_action_redirect = reverse_lazy(
        viewname='importer:import_setup_list'
    )
    success_message = _('%(count)d import setup cleared.')
    success_message_plural = _('%(count)d import setups cleared.')

    def get_extra_context(self):
        queryset = self.object_list

        result = {
            'title': ungettext(
                singular='Clear the selected import setup?',
                plural='Clear the selected import setups?',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Clear import setup: %s') % queryset.first()
                }
            )

        return result

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }

    def object_action(self, instance, form=None):
        instance.clear()


class ImportSetupListView(SingleObjectListView):
    model = ImportSetup
    object_permission = permission_import_setup_view

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_import_setup_list,
            'no_results_main_link': link_import_setup_backend_selection.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Import setups are configuration units that will retrieve '
                'files for external locations and create documents from '
                'them.'
            ),
            'no_results_title': _('No import setups available'),
            'title': _('Import setups'),
        }


class ImportSetupPopulateView(MultipleObjectConfirmActionView):
    model = ImportSetup
    object_permission = permission_import_setup_process
    pk_url_kwarg = 'import_setup_id'
    post_action_redirect = reverse_lazy(
        viewname='importer:import_setup_list'
    )
    success_message = _('%(count)d import setup preparation queued.')
    success_message_plural = _('%(count)d import setups preparation queued.')

    def get_extra_context(self):
        queryset = self.object_list

        result = {
            'message': _(
                'This process will run in the background. Depending on the '
                'number of files that match the import setup criteria, '
                'the import backend, the size of the source repository, '
                'and the bandwidth between Mayan EDMS and the source '
                'repository, it may take between a few minutes to a few '
                'days for the entire preparation process to complete.'
            ),
            'title': ungettext(
                singular='Prepare the selected import setup?',
                plural='Prepare the selected import setups?',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Prepare import setup: %s') % queryset.first()
                }
            )

        return result

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }

    def object_action(self, instance, form=None):
        task_import_setup_populate.apply_async(
            kwargs={'import_setup_id': instance.pk}
        )


class ImportSetupProcessView(MultipleObjectConfirmActionView):
    model = ImportSetup
    object_permission = permission_import_setup_process
    pk_url_kwarg = 'import_setup_id'
    post_action_redirect = reverse_lazy(
        viewname='importer:import_setup_list'
    )
    success_message = _('%(count)d import setup processing queued.')
    success_message_plural = _('%(count)d import setups processing queued.')

    def get_extra_context(self):
        queryset = self.object_list

        result = {
            'title': ungettext(
                singular='Process the selected import setup?',
                plural='Process the selected import setups?',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Process import setup: %s') % queryset.first()
                }
            )

        return result

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }

    def object_action(self, instance, form=None):
        if instance.items.count() == 0:
            messages.warning(
                message=_(
                    'Import setup "%s" does not have any item to process. '
                    'Use the prepare action first.'
                ) % instance, request=self.request
            )
        else:
            task_import_setup_process.apply_async(
                kwargs={'import_setup_id': instance.pk}
            )


class ImportSetupItemDeleteView(MultipleObjectConfirmActionView):
    model = ImportSetupItem
    object_permission = permission_import_setup_edit
    pk_url_kwarg = 'import_setup_item_id'
    success_message = _('%(count)d import setup item deleted.')
    success_message_plural = _('%(count)d import setup items deleted.')

    def get_extra_context(self):
        queryset = self.object_list

        result = {
            'delete_view': True,
            'import_setup': self.object_list.first().import_setup,
            'message': _(
                'You can add this item again by executing the prepare '
                'action.'
            ),
            'navigation_object_list': ('import_setup', 'object'),
            'title': ungettext(
                singular='Delete the selected import setup item?',
                plural='Delete the selected import setup items?',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Delete import setup item: %s') % queryset.first()
                }
            )

        return result

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }

    def get_post_action_redirect(self):
        # Use [0] instead of first(). First returns None and it is not usable.
        return reverse(
            viewname='importer:import_setup_items_list', kwargs={
                'import_setup_id': self.object_list[0].import_setup.pk
            }
        )

    def object_action(self, instance, form=None):
        instance.delete()


class ImportSetupItemDocumentListView(
    ExternalObjectViewMixin, DocumentListView
):
    external_object_class = ImportSetupItem
    external_object_permission = permission_import_setup_view
    external_object_pk_url_kwarg = 'import_setup_item_id'

    def get_document_queryset(self):
        return self.external_object.documents.all()

    def get_extra_context(self):
        context = super().get_extra_context()
        context.update(
            {
                'import_setup': self.external_object.import_setup,
                'import_setup_item': self.external_object,
                'navigation_object_list': (
                    'import_setup', 'import_setup_item'
                ),
                'no_results_text': _(
                    'This view will list the documents that were created '
                    'by an import setup item.'
                ),
                'no_results_title': _(
                    'There are no documents for this import setup item.'
                ),
                'title': _(
                    'Document created from import setup item: %s'
                ) % self.external_object,
            }
        )
        return context


class ImportSetupItemListView(ExternalObjectViewMixin, SingleObjectListView):
    external_object_class = ImportSetup
    external_object_permission = permission_import_setup_view
    external_object_pk_url_kwarg = 'import_setup_id'

    def get_extra_context(self):
        return {
            'hide_link': True,
            'hide_object': True,
            'no_results_icon': icon_import_setup_items_list,
            'no_results_main_link': link_import_setup_populate.resolve(
                context=RequestContext(
                    dict_={'object': self.external_object},
                    request=self.request
                )
            ),
            'no_results_text': _(
                'Import setups items are the entries for the actual '
                'files that will be imported and converted into documents.'
            ),
            'no_results_title': _('No import setups items available'),
            'object': self.external_object,
            'title': _('Items of import setup: %s') % self.external_object,
        }

    def get_source_queryset(self):
        return self.external_object.items.all()


class ImportSetupItemProcessView(MultipleObjectConfirmActionView):
    model = ImportSetupItem
    object_permission = permission_import_setup_process
    pk_url_kwarg = 'import_setup_item_id'
    success_message = _('%(count)d import setup item processed.')
    success_message_plural = _('%(count)d import setup items processed.')

    def get_extra_context(self):
        queryset = self.object_list

        result = {
            'import_setup': self.object_list.first().import_setup,
            'navigation_object_list': ('import_setup', 'object'),
            'title': ungettext(
                singular='Process the selected import setup item?',
                plural='Process the selected import setup items?',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result.update(
                {
                    'object': queryset.first(),
                    'title': _('Process import setup item: %s') % queryset.first()
                }
            )

        return result

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }

    def get_post_action_redirect(self):
        # Use [0] instead of first(). First returns None and it is not usable.
        return reverse(
            viewname='importer:import_setup_items_list', kwargs={
                'import_setup_id': self.object_list[0].import_setup.pk
            }
        )

    def object_action(self, instance, form=None):
        task_import_setup_item_process.apply_async(
            kwargs={
                'import_setup_item_id': instance.pk
            }
        )


class ImportSetupItemLoadView(ExternalObjectViewMixin, FormView):
    external_object_class = ImportSetup
    external_object_object_permission = permission_model_filer_load
    external_object_pk_url_kwarg = 'import_setup_id'
    form_class = ModelFilerUpload

    def form_valid(self, form):
        with self.request.FILES['uploaded_file'].open(mode='r') as file_object:
            shared_upload_file = SharedUploadedFile.objects.create(
                file=File(file_object),
            )

        full_model_name = ModelFiler.get_full_model_name(
            model=self.external_object.items.model
        )
        task = task_model_filer_load.apply_async(
            kwargs={
                'field_defaults': {'import_setup_id': self.external_object.pk},
                'full_model_name': full_model_name,
                'shared_upload_file_id': shared_upload_file.pk
            }
        )
        self.shared_upload_file_id = task.get()

        messages.success(
            message=_('File uploaded and queued for loading as models.'),
            request=self.request
        )
        return HttpResponseRedirect(
            redirect_to=reverse(viewname='importer:import_setup_list')
        )

    def get_extra_context(self):
        return {
            'object': self.get_external_object(),
            'title': _(
                'Load the items of import setup: %s'
            ) % self.get_external_object()
        }

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }


class ImportSetupItemSaveConfirmView(ExternalObjectViewMixin, ConfirmView):
    external_object_class = ImportSetup
    external_object_object_permission = permission_model_filer_save
    external_object_pk_url_kwarg = 'import_setup_id'

    def get_extra_context(self):
        return {
            'object': self.get_external_object(),
            'title': _(
                'Save the items of import setup: %s'
            ) % self.get_external_object()
        }

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user,
        }

    def get_success_url(self):
        return reverse(
            viewname='importer:import_setup_save_download', kwargs={
                'shared_upload_file_id': self.shared_upload_file_id
            }
        )

    def view_action(self):
        full_model_name = ModelFiler.get_full_model_name(
            model=self.external_object.items.model
        )

        task = task_model_filer_save.apply_async(
            kwargs={
                'filter_kwargs': {'import_setup': self.external_object.pk},
                'full_model_name': full_model_name,
            }
        )
        self.shared_upload_file_id = task.get()


class ImportSetupItemSaveDownloadView(SingleObjectDownloadView):
    model = SharedUploadedFile
    pk_url_kwarg = 'shared_upload_file_id'

    def get_download_filename(self):
        return '{}.csv'.format(self.object)


class ImportSetupLogListView(ExternalObjectViewMixin, SingleObjectListView):
    external_object_class = ImportSetup
    external_object_permission = permission_import_setup_view
    external_object_pk_url_kwarg = 'import_setup_id'

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_import_setup_log_list,
            'no_results_text': _(
                'This view displays the error log for import setups. '
                'An empty list is a good thing.'
            ),
            'no_results_title': _(
                'There are no error log entries'
            ),
            'object': self.external_object,
            'title': _(
                'Log entries for import setup: %s'
            ) % self.external_object,
        }

    def get_source_queryset(self):
        return self.external_object.logs.all()
