from django.conf.urls import url

from .api_views import (
    APIStoredCredentialListView, APIStoredCredentialDetailView
)
from .views import (
    StoredCredentialBackendSelectionView, StoredCredentialCreateView,
    StoredCredentialDeleteView, StoredCredentialEditView,
    StoredCredentialListView
)


urlpatterns = [
    url(
        regex=r'^credentials/backend/selection/$',
        name='stored_credential_backend_selection',
        view=StoredCredentialBackendSelectionView.as_view()
    ),
    url(
        regex=r'^credentials/(?P<class_path>[a-zA-Z0-9_.]+)/create/$',
        name='stored_credential_create',
        view=StoredCredentialCreateView.as_view()
    ),
    url(
        regex=r'^credentials/(?P<stored_credential_id>\d+)/delete/$',
        name='stored_credential_delete',
        view=StoredCredentialDeleteView.as_view()
    ),
    url(
        regex=r'^credentials/(?P<stored_credential_id>\d+)/edit/$',
        name='stored_credential_edit', view=StoredCredentialEditView.as_view()
    ),
    url(
        regex=r'^credentials/$', name='stored_credential_list',
        view=StoredCredentialListView.as_view()
    )
]

api_urls = [
    url(
        regex=r'^credentials/$', name='credential-list',
        view=APIStoredCredentialListView.as_view()
    ),
    url(
        regex=r'^credentials/(?P<credential_id>[0-9]+)/$',
        name='credential-detail', view=APIStoredCredentialDetailView.as_view()
    ),
]
