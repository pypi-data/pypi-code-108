from actstream.models import Action
from rest_framework import status

from mayan.apps.events.tests.mixins import EventTestCaseMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..events import event_credential_created, event_credential_edited
from ..models import StoredCredential
from ..permissions import (
    permission_credential_create, permission_credential_delete,
    permission_credential_edit, permission_credential_view
)
from .mixins import (
    StoredCredentialAPIViewTestMixin, StoredCredentialTestMixin
)


class StoredCredentialAPIViewTestCase(
    EventTestCaseMixin, StoredCredentialAPIViewTestMixin,
    StoredCredentialTestMixin, BaseAPITestCase
):
    _test_event_object_name = 'test_stored_credential'

    # TODO: Remove this backport after move to version 3.5.
    def _clear_events(self):
        Action.objects.all().delete()

    def test_credential_create_api_view_no_permission(self):
        credential_count = StoredCredential.objects.count()

        self._clear_events()

        response = self._request_test_stored_credential_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(StoredCredential.objects.count(), credential_count)

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_credential_create_api_view_with_access(self):
        credential_count = StoredCredential.objects.count()

        self.grant_permission(permission=permission_credential_create)

        self._clear_events()

        response = self._request_test_stored_credential_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            StoredCredential.objects.count(), credential_count + 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event.actor, self.test_stored_credential)
        self.assertEqual(event.target, self.test_stored_credential)
        self.assertEqual(event.verb, event_credential_created.id)

    def test_credential_delete_api_view_no_permission(self):
        self._create_test_stored_credential()

        credential_count = StoredCredential.objects.count()

        self._clear_events()

        response = self._request_test_stored_credential_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            StoredCredential.objects.count(), credential_count
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_credential_delete_api_view_with_access(self):
        self._create_test_stored_credential()

        credential_count = StoredCredential.objects.count()

        self.grant_access(
            obj=self.test_stored_credential,
            permission=permission_credential_delete
        )

        self._clear_events()

        response = self._request_test_stored_credential_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            StoredCredential.objects.count(), credential_count - 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_credential_detail_api_view_no_permission(self):
        self._create_test_stored_credential()

        self._clear_events()

        response = self._request_test_stored_credential_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('id' not in response.data)

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_credential_detail_api_view_with_access(self):
        self._create_test_stored_credential()

        self.grant_access(
            obj=self.test_stored_credential,
            permission=permission_credential_view
        )

        self._clear_events()

        response = self._request_test_stored_credential_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['id'], self.test_stored_credential.pk
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_credential_edit_via_patch_api_view_no_permssion(self):
        self._create_test_stored_credential()

        credential_label = self.test_stored_credential.label

        self._clear_events()

        response = self._request_test_stored_credential_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_stored_credential.refresh_from_db()
        self.assertEqual(
            self.test_stored_credential.label, credential_label
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_credential_edit_via_patch_api_view_with_access(self):
        self._create_test_stored_credential()

        credential_label = self.test_stored_credential.label

        self.grant_access(
            obj=self.test_stored_credential,
            permission=permission_credential_edit
        )

        self._clear_events()

        response = self._request_test_stored_credential_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_stored_credential.refresh_from_db()
        self.assertNotEqual(
            self.test_stored_credential.label, credential_label
        )

        event = self._get_test_object_event()
        self.assertEqual(event.actor, self.test_stored_credential)
        self.assertEqual(event.target, self.test_stored_credential)
        self.assertEqual(event.verb, event_credential_edited.id)

    def test_credential_list_api_view_no_permission(self):
        self._create_test_stored_credential()

        self._clear_events()

        response = self._request_test_stored_credential_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_credential_list_api_view_with_access(self):
        self._create_test_stored_credential()

        self.grant_access(
            obj=self.test_stored_credential,
            permission=permission_credential_view
        )

        self._clear_events()

        response = self._request_test_stored_credential_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['id'], self.test_stored_credential.pk
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)
