from actstream.models import Action
from rest_framework import status

from credentials.tests.mixins import StoredCredentialTestMixin
from mayan.apps.documents.tests.mixins import DocumentTestMixin
from mayan.apps.rest_api.tests.base import BaseAPITestCase

from ..events import event_import_setup_created, event_import_setup_edited
from ..models import ImportSetup
from ..permissions import (
    permission_import_setup_create, permission_import_setup_delete,
    permission_import_setup_edit, permission_import_setup_process,
    permission_import_setup_view
)
from .mixins import (
    EventTestCaseMixin, ImportSetupAPIViewTestMixin, ImportSetupItemTestMixin,
    ImportSetupTestMixin
)


class ImportSetupAPIViewTestCase(
    DocumentTestMixin, EventTestCaseMixin, ImportSetupAPIViewTestMixin,
    ImportSetupTestMixin, BaseAPITestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    # TODO: Remove this backport after move to version 3.5.
    def _clear_events(self):
        Action.objects.all().delete()

    def test_import_setup_create_api_view_no_permission(self):
        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_create_api_view_with_access(self):
        import_setup_count = ImportSetup.objects.count()

        self.grant_permission(permission=permission_import_setup_create)

        self._clear_events()

        response = self._request_test_import_setup_create_api_view()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count + 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event.actor, self.test_import_setup)
        self.assertEqual(event.target, self.test_import_setup)
        self.assertEqual(event.verb, event_import_setup_created.id)

    def test_import_setup_delete_api_view_no_permission(self):
        self._create_test_import_setup()

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_delete_api_view_with_access(self):
        self._create_test_import_setup()

        import_setup_count = ImportSetup.objects.count()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_delete
        )

        self._clear_events()

        response = self._request_test_import_setup_delete_api_view()
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count - 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_detail_api_view_no_permission(self):
        self._create_test_import_setup()

        self._clear_events()

        response = self._request_test_import_setup_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue('id' not in response.data)

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_detail_api_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_view
        )

        self._clear_events()

        response = self._request_test_import_setup_detail_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['id'], self.test_import_setup.pk
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_edit_via_patch_api_view_no_permssion(self):
        self._create_test_import_setup()

        import_setup_label = self.test_import_setup.label

        self._clear_events()

        response = self._request_test_import_setup_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.test_import_setup.refresh_from_db()
        self.assertEqual(
            self.test_import_setup.label, import_setup_label
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_edit_via_patch_api_view_with_access(self):
        self._create_test_import_setup()

        import_setup_label = self.test_import_setup.label

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )

        self._clear_events()

        response = self._request_test_import_setup_edit_via_patch_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.test_import_setup.refresh_from_db()
        self.assertNotEqual(
            self.test_import_setup.label, import_setup_label
        )

        event = self._get_test_object_event()
        self.assertEqual(event.actor, self.test_import_setup)
        self.assertEqual(event.target, self.test_import_setup)
        self.assertEqual(event.verb, event_import_setup_edited.id)

    def test_import_setup_list_api_view_no_permission(self):
        self._create_test_import_setup()

        self._clear_events()

        response = self._request_test_import_setup_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_list_api_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_view
        )

        self._clear_events()

        response = self._request_test_import_setup_list_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['results'][0]['id'], self.test_import_setup.pk
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)


class ImportSetupItemAPIViewTestMixin:
    def _request_test_import_setup_clear_api_view(self):
        return self.post(
            viewname='rest_api:importsetup-clear', kwargs={
                'import_setup_id': self.test_import_setup.pk
            }
        )

    def _request_test_import_setup_populate_api_view(self):
        return self.post(
            viewname='rest_api:importsetup-populate', kwargs={
                'import_setup_id': self.test_import_setup.pk
            }
        )

    def _request_test_import_setup_process_api_view(self):
        return self.post(
            viewname='rest_api:importsetup-process', kwargs={
                'import_setup_id': self.test_import_setup.pk
            }
        )


class ImportSetupActionAPIViewTestCase(
    DocumentTestMixin, EventTestCaseMixin, ImportSetupItemAPIViewTestMixin,
    ImportSetupTestMixin, ImportSetupItemTestMixin,
    StoredCredentialTestMixin, BaseAPITestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_stored_credential()
        self._create_test_import_setup()

    def test_import_setup_clear_api_view_no_perimssion(self):
        self._create_test_import_setup_item()

        import_setup_item_count = self.test_import_setup.items.count()

        response = self._request_test_import_setup_clear_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count
        )

    def test_import_setup_clear_api_view_with_access(self):
        self._create_test_import_setup_item()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )

        import_setup_item_count = self.test_import_setup.items.count()

        response = self._request_test_import_setup_clear_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count - 1
        )

    def test_import_setup_populate_api_view_no_permission(self):
        import_setup_item_count = self.test_import_setup.items.count()

        response = self._request_test_import_setup_populate_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count
        )

    def test_import_setup_populate_api_view_with_access(self):
        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )

        import_setup_item_count = self.test_import_setup.items.count()

        response = self._request_test_import_setup_populate_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count + 1
        )

    def test_import_setup_process_api_view_no_access(self):
        self._create_test_import_setup_item()

        document_count = self.test_document_type.documents.count()

        response = self._request_test_import_setup_process_api_view()
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertEqual(
            self.test_document_type.documents.count(), document_count
        )

    def test_import_setup_process_api_view_with_access(self):
        self._create_test_import_setup_item()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )
        document_count = self.test_document_type.documents.count()

        response = self._request_test_import_setup_process_api_view()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(
            self.test_document_type.documents.count(), document_count + 1
        )
