from mayan.apps.common.tests.base import GenericViewTestCase
from mayan.apps.documents.tests.mixins import DocumentTestMixin

from credentials.tests.mixins import StoredCredentialTestMixin

from ..events import (
    event_import_setup_created, event_import_setup_edited,
    event_import_setup_item_completed, event_import_setup_populate_ended,
    event_import_setup_populate_started, event_import_setup_process_ended,
    event_import_setup_process_started
)
from ..models import ImportSetup, ImportSetupAction
from ..permissions import (
    permission_import_setup_create, permission_import_setup_delete,
    permission_import_setup_edit, permission_import_setup_process,
    permission_import_setup_view
)

from .mixins import (
    EventTestCaseMixin, ImportSetupActionTestMixin,
    ImportSetupActionViewTestMixin, ImportSetupTestMixin,
    ImportSetupItemTestMixin, ImportSetupViewTestMixin,
    ImportSetupItemViewTestMixin
)


class ImportSetupActionViewTestCase(
    StoredCredentialTestMixin, DocumentTestMixin, EventTestCaseMixin,
    ImportSetupActionTestMixin, ImportSetupActionViewTestMixin,
    ImportSetupTestMixin, GenericViewTestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_stored_credential()
        self._create_test_import_setup()

    def test_import_setup_action_backend_selection_view_no_permissions(self):
        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_backend_selection_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_action_backend_selection_view_with_permissions(self):
        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )
        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_backend_selection_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_action_create_view_no_permissions(self):
        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_create_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_action_create_view_with_permissions(self):
        self.grant_access(
            obj=self.test_import_setup, permission=permission_import_setup_edit
        )
        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count + 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_action_delete_view_no_permissions(self):
        self._create_test_import_setup_action()

        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_action_delete_view_with_access(self):
        self._create_test_import_setup_action()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )

        import_setup_action_count = ImportSetupAction.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_action_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetupAction.objects.count(), import_setup_action_count - 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_action_edit_view_no_permissions(self):
        self._create_test_import_setup_action()

        import_setup_action_label = self.test_import_setup_action.label

        self._clear_events()

        response = self._request_test_import_setup_action_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_import_setup_action.refresh_from_db()
        self.assertEqual(
            self.test_import_setup_action.label, import_setup_action_label
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_action_edit_view_with_access(self):
        self._create_test_import_setup_action()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )

        self._clear_events()

        import_setup_action_label = self.test_import_setup_action.label

        response = self._request_test_import_setup_action_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_import_setup_action.refresh_from_db()
        self.assertNotEqual(
            self.test_import_setup_action.label, import_setup_action_label
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_action_list_view_with_no_permission(self):
        self._create_test_import_setup_action()

        self._clear_events()

        response = self._request_test_import_setup_action_list_view()
        self.assertNotContains(
            response=response, text=self.test_import_setup_action.label,
            status_code=404
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_action_list_view_with_access(self):
        self._create_test_import_setup_action()

        self.grant_access(
            obj=self.test_import_setup, permission=permission_import_setup_view
        )

        self._clear_events()

        response = self._request_test_import_setup_action_list_view()
        self.assertContains(
            response=response, text=self.test_import_setup_action.label,
            status_code=200
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)


class ImportSetupViewTestCase(
    StoredCredentialTestMixin, DocumentTestMixin, EventTestCaseMixin,
    ImportSetupTestMixin, ImportSetupViewTestMixin, GenericViewTestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_stored_credential()

    def test_import_setup_backend_selection_view_no_permissions(self):
        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_backend_selection_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_backend_selection_view_with_permissions(self):
        self.grant_permission(permission=permission_import_setup_create)

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_backend_selection_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_create_view_no_permissions(self):
        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_create_view()
        self.assertEqual(response.status_code, 403)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        events = self._get_test_events()
        self.assertEqual(events.count(), 0)

    def test_import_setup_create_view_with_permissions(self):
        self.grant_permission(permission=permission_import_setup_create)

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_create_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count + 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event.actor, self._test_case_user)
        self.assertEqual(event.target, self.test_import_setup)
        self.assertEqual(event.verb, event_import_setup_created.id)

    def test_import_setup_delete_view_no_permissions(self):
        self._create_test_import_setup()

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_delete_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(ImportSetup.objects.count(), import_setup_count)

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_delete_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_delete
        )

        import_setup_count = ImportSetup.objects.count()

        self._clear_events()

        response = self._request_test_import_setup_delete_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            ImportSetup.objects.count(), import_setup_count - 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_edit_view_no_permissions(self):
        self._create_test_import_setup()

        import_setup_label = self.test_import_setup.label

        self._clear_events()

        response = self._request_test_import_setup_edit_view()
        self.assertEqual(response.status_code, 404)

        self.test_import_setup.refresh_from_db()
        self.assertEqual(self.test_import_setup.label, import_setup_label)

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_edit_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_edit
        )

        import_setup_label = self.test_import_setup.label

        self._clear_events()

        response = self._request_test_import_setup_edit_view()
        self.assertEqual(response.status_code, 302)

        self.test_import_setup.refresh_from_db()
        self.assertNotEqual(self.test_import_setup.label, import_setup_label)

        event = self._get_test_object_event()
        self.assertEqual(event.actor, self._test_case_user)
        self.assertEqual(event.target, self.test_import_setup)
        self.assertEqual(event.verb, event_import_setup_edited.id)

    def test_import_setup_list_view_with_no_permission(self):
        self._create_test_import_setup()

        self._clear_events()

        response = self._request_test_import_setup_list_view()
        self.assertNotContains(
            response=response, text=self.test_import_setup.label,
            status_code=200
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_list_view_with_access(self):
        self._create_test_import_setup()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_view
        )

        self._clear_events()

        response = self._request_test_import_setup_list_view()
        self.assertContains(
            response=response, text=self.test_import_setup.label,
            status_code=200
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)


class ImportSetupItemViewTestCase(
    StoredCredentialTestMixin, DocumentTestMixin, EventTestCaseMixin,
    ImportSetupTestMixin, ImportSetupItemTestMixin,
    ImportSetupItemViewTestMixin, GenericViewTestCase
):
    _test_event_object_name = 'test_import_setup'
    auto_upload_test_document = False

    def setUp(self):
        super().setUp()
        self._create_test_stored_credential()
        self._create_test_import_setup()

    def test_import_setup_clear_view_no_permission(self):
        self._create_test_import_setup_item()

        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_clear_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_clear_view_with_access(self):
        self._create_test_import_setup_item()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )

        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_clear_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count - 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_populate_view_no_permission(self):
        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_populate_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_populate_view_with_access(self):
        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )

        import_setup_item_count = self.test_import_setup.items.count()

        self._clear_events()

        response = self._request_test_import_setup_populate_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_import_setup.items.count(), import_setup_item_count + 1
        )

        event = self._get_test_object_event()
        self.assertEqual(event.actor, self.test_import_setup)
        self.assertEqual(event.target, self.test_import_setup)
        self.assertEqual(event.verb, event_import_setup_populate_ended.id)

    def test_import_setup_process_view_no_permission(self):
        self._create_test_import_setup_item()

        document_count = self.test_document_type.documents.count()

        self._clear_events()

        response = self._request_test_import_setup_process_view()
        self.assertEqual(response.status_code, 404)

        self.assertEqual(
            self.test_document_type.documents.count(), document_count
        )

        event = self._get_test_object_event()
        self.assertEqual(event, None)

    def test_import_setup_process_view_with_access(self):
        self._create_test_import_setup_item()

        self.grant_access(
            obj=self.test_import_setup,
            permission=permission_import_setup_process
        )
        document_count = self.test_document_type.documents.count()

        self._clear_events()

        response = self._request_test_import_setup_process_view()
        self.assertEqual(response.status_code, 302)

        self.assertEqual(
            self.test_document_type.documents.count(), document_count + 1
        )

        events = self._get_test_object_events()
        self.assertEqual(events[0].actor, self.test_import_setup)
        self.assertEqual(events[0].target, self.test_import_setup)
        self.assertEqual(events[0].verb, event_import_setup_process_started.id)

        self.assertEqual(events[1].action_object, self.test_import_setup)
        self.assertEqual(events[1].actor, self.test_import_setup_item)
        self.assertEqual(events[1].target, self.test_import_setup_item)
        self.assertEqual(events[1].verb, event_import_setup_item_completed.id)

        self.assertEqual(events[2].actor, self.test_import_setup)
        self.assertEqual(events[2].target, self.test_import_setup)
        self.assertEqual(events[2].verb, event_import_setup_process_ended.id)
