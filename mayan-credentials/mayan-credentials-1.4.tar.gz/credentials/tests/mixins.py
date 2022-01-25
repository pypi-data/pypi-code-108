from django.db.models import Q

from ..models import StoredCredential

from .literals import (
    TEST_STORED_CREDENTIAL_BACKEND_DATA_FIELDS,
    TEST_STORED_CREDENTIAL_BACKEND_DATA, TEST_STORED_CREDENTIAL_BACKEND_PATH,
    TEST_STORED_CREDENTIAL_LABEL, TEST_STORED_CREDENTIAL_LABEL_EDITED
)


class StoredCredentialAPIViewTestMixin:
    def _request_test_stored_credential_create_api_view(self):
        pk_list = list(StoredCredential.objects.values_list('pk', flat=True))

        response = self.post(
            viewname='rest_api:credential-list', data={
                'label': TEST_STORED_CREDENTIAL_LABEL,
                'backend_path': TEST_STORED_CREDENTIAL_BACKEND_PATH,
                'backend_data': TEST_STORED_CREDENTIAL_BACKEND_DATA
            }
        )

        try:
            self.test_stored_credential = StoredCredential.objects.get(
                ~Q(pk__in=pk_list)
            )
        except StoredCredential.DoesNotExist:
            self.test_stored_credential = None

        return response

    def _request_test_stored_credential_delete_api_view(self):
        return self.delete(
            viewname='rest_api:credential-detail', kwargs={
                'credential_id': self.test_stored_credential.pk
            }
        )

    def _request_test_stored_credential_detail_api_view(self):
        return self.get(
            viewname='rest_api:credential-detail', kwargs={
                'credential_id': self.test_stored_credential.pk
            }
        )

    def _request_test_stored_credential_edit_via_patch_api_view(self):
        return self.patch(
            viewname='rest_api:credential-detail', kwargs={
                'credential_id': self.test_stored_credential.pk
            }, data={
                'label': '{} edited'.format(self.test_stored_credential.label)
            }
        )

    def _request_test_stored_credential_list_api_view(self):
        return self.get(viewname='rest_api:credential-list')


class StoredCredentialTestMixin(object):
    def _create_test_stored_credential(self):
        self.test_stored_credential = StoredCredential.objects.create(
            label=TEST_STORED_CREDENTIAL_LABEL,
            backend_path=TEST_STORED_CREDENTIAL_BACKEND_PATH,
            backend_data=TEST_STORED_CREDENTIAL_BACKEND_DATA
        )


class StoredCredentialViewTestMixin(object):
    def _request_test_stored_credential_backend_selection_view(self):
        return self.post(
            viewname='credentials:stored_credential_backend_selection', data={
                'backend': TEST_STORED_CREDENTIAL_BACKEND_PATH,
            }
        )

    def _request_test_stored_credential_create_view(self):
        data = {'label': TEST_STORED_CREDENTIAL_LABEL}
        data.update(TEST_STORED_CREDENTIAL_BACKEND_DATA_FIELDS)

        return self.post(
            viewname='credentials:stored_credential_create', kwargs={
                'class_path': TEST_STORED_CREDENTIAL_BACKEND_PATH,
            }, data=data
        )

    def _request_test_stored_credential_delete_view(self):
        return self.post(
            viewname='credentials:stored_credential_delete', kwargs={
                'stored_credential_id': self.test_stored_credential.pk
            }
        )

    def _request_test_stored_credential_edit_view(self):
        data = {'label': TEST_STORED_CREDENTIAL_LABEL_EDITED}
        data.update(TEST_STORED_CREDENTIAL_BACKEND_DATA_FIELDS)

        return self.post(
            viewname='credentials:stored_credential_edit', kwargs={
                'stored_credential_id': self.test_stored_credential.pk
            }, data=data
        )

    def _request_test_stored_credential_list_view(self):
        return self.get(viewname='credentials:stored_credential_list')
