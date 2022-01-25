import logging

from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.views.generics import (
    FormView, SingleObjectDeleteView, SingleObjectDynamicFormCreateView,
    SingleObjectDynamicFormEditView, SingleObjectListView
)

from .classes import CredentialBackend
from .forms import (
    StoredCredentialBackendDynamicForm, StoredCredentialBackendSelectionForm
)
from .icons import icon_credentials
from .links import link_stored_credential_backend_selection
from .models import StoredCredential
from .permissions import (
    permission_credential_create, permission_credential_delete,
    permission_credential_edit, permission_credential_view
)

logger = logging.getLogger(name=__name__)


class StoredCredentialBackendSelectionView(FormView):
    extra_context = {
        'title': _('New credential backend selection'),
    }
    form_class = StoredCredentialBackendSelectionForm
    view_permission = permission_credential_create

    def form_valid(self, form):
        backend = form.cleaned_data['backend']
        return HttpResponseRedirect(
            redirect_to=reverse(
                viewname='credentials:stored_credential_create', kwargs={
                    'class_path': backend
                }
            )
        )


class StoredCredentialCreateView(SingleObjectDynamicFormCreateView):
    form_class = StoredCredentialBackendDynamicForm
    post_action_redirect = reverse_lazy(
        viewname='credentials:stored_credential_list'
    )
    view_permission = permission_credential_create

    def get_backend(self):
        try:
            return CredentialBackend.get(name=self.kwargs['class_path'])
        except KeyError:
            raise Http404(
                '{} class not found'.format(self.kwargs['class_path'])
            )

    def get_extra_context(self):
        return {
            'title': _(
                'Create a "%s" credential'
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


class StoredCredentialDeleteView(SingleObjectDeleteView):
    model = StoredCredential
    object_permission = permission_credential_delete
    pk_url_kwarg = 'stored_credential_id'
    post_action_redirect = reverse_lazy(
        viewname='credentials:stored_credential_list'
    )

    def get_extra_context(self):
        return {
            'title': _('Delete credential: %s') % self.object,
        }


class StoredCredentialEditView(SingleObjectDynamicFormEditView):
    form_class = StoredCredentialBackendDynamicForm
    model = StoredCredential
    object_permission = permission_credential_edit
    pk_url_kwarg = 'stored_credential_id'

    def get_extra_context(self):
        return {
            'object': self.object,
            'title': _('Edit credential: %s') % self.object,
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


class StoredCredentialListView(SingleObjectListView):
    model = StoredCredential
    object_permission = permission_credential_view

    def get_extra_context(self):
        return {
            'hide_object': True,
            'no_results_icon': icon_credentials,
            'no_results_main_link': link_stored_credential_backend_selection.resolve(
                context=RequestContext(request=self.request)
            ),
            'no_results_text': _(
                'Credentials represent an identify. '
                'These are used to when accessing external systems or '
                'services.'
            ),
            'no_results_title': _('No credentials available'),
            'title': _('Credentials'),
        }

    def get_form_schema(self):
        return {'fields': self.get_backend().fields}
