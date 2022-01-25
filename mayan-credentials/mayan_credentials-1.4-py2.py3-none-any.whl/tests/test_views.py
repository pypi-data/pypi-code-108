from mayan.apps.common.tests.base import GenericViewTestCase

from ..models import StoredCredential
from ..permissions import (
    permission_credential_create, permission_credential_delete,
    permission_credential_edit, permission_credential_view
)

from .mixins import StoredCredentialTestMixin, StoredCredentialViewTestMixin


class CredentialViewTestCase(
    StoredCredentialTestMixin, StoredCredentialViewTestMixin,
    GenericViewTestCase
):
    def test_stored_credential_backend_selection_view_no_permissions(self):
        credential_count = StoredCredential.objects.count()

        response = self._request_test_stored_credential_backend_selection_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(StoredCredential.objects.count(), credential_count)

    def test_stored_credential_backend_selection_view_with_permissions(self):
        self.grant_permission(permission=permission_credential_create)

        credential_count = StoredCredential.objects.count()

        response = self._request_test_stored_credential_backend_selection_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(StoredCredential.objects.count(), credential_count)

    def test_stored_credential_create_view_no_permissions(self):
        credential_count = StoredCredential.objects.count()

        response = self._request_test_stored_credential_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(StoredCredential.objects.count(), credential_count)

    def test_stored_credential_create_view_with_permissions(self):
        self.grant_permission(permission=permission_credential_create)

        credential_count = StoredCredential.objects.count()

        response = self._request_test_stored_credential_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            StoredCredential.objects.count(), credential_count + 1
        )

    def test_stored_credential_delete_view_no_permissions(self):
        self._create_test_stored_credential()

        credential_count = StoredCredential.objects.count()

        response = self._request_test_stored_credential_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(StoredCredential.objects.count(), credential_count)

    def test_stored_credential_delete_view_with_access(self):
        self._create_test_stored_credential()

        self.grant_access(
            obj=self.test_stored_credential,
            permission=permission_credential_delete
        )

        credential_count = StoredCredential.objects.count()

        response = self._request_test_stored_credential_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            StoredCredential.objects.count(), credential_count - 1
        )

    def test_stored_credential_edit_view_no_permissions(self):
        self._create_test_stored_credential()

        credential_label = self.test_stored_credential.label

        response = self._request_test_stored_credential_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_stored_credential.refresh_from_db()
        self.assertEqual(self.test_stored_credential.label, credential_label)

    def test_stored_credential_edit_view_with_access(self):
        self._create_test_stored_credential()

        self.grant_access(
            obj=self.test_stored_credential,
            permission=permission_credential_edit
        )

        credential_label = self.test_stored_credential.label

        response = self._request_test_stored_credential_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_stored_credential.refresh_from_db()
        self.assertNotEqual(
            self.test_stored_credential.label, credential_label
        )

    def test_stored_credential_list_view_with_no_permission(self):
        self._create_test_stored_credential()

        response = self._request_test_stored_credential_list_view()
        self.assertNotContains(
            response=response, text=self.test_stored_credential.label,
            status_code=200
        )

    def test_stored_credential_list_view_with_access(self):
        self._create_test_stored_credential()

        self.grant_access(
            obj=self.test_stored_credential,
            permission=permission_credential_view
        )

        response = self._request_test_stored_credential_list_view()
        self.assertContains(
            response=response, text=self.test_stored_credential.label,
            status_code=200
        )
