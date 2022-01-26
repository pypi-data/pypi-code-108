from unittest.mock import MagicMock

class AuditsApiMock:

    def __init__(self):
        self.mock_bulk_create_events = MagicMock()
        self.mock_create_audit_destination = MagicMock()
        self.mock_delete_audit_destination = MagicMock()
        self.mock_get_audit_destination = MagicMock()
        self.mock_list_audit_destinations = MagicMock()
        self.mock_list_audits = MagicMock()
        self.mock_list_auth_records = MagicMock()
        self.mock_replace_audit_destination = MagicMock()

    def bulk_create_events(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.bulk_create_events with MagicMock.
        """
        return self.mock_bulk_create_events(self, *args, **kwargs)

    def create_audit_destination(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.create_audit_destination with MagicMock.
        """
        return self.mock_create_audit_destination(self, *args, **kwargs)

    def delete_audit_destination(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.delete_audit_destination with MagicMock.
        """
        return self.mock_delete_audit_destination(self, *args, **kwargs)

    def get_audit_destination(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.get_audit_destination with MagicMock.
        """
        return self.mock_get_audit_destination(self, *args, **kwargs)

    def list_audit_destinations(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.list_audit_destinations with MagicMock.
        """
        return self.mock_list_audit_destinations(self, *args, **kwargs)

    def list_audits(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.list_audits with MagicMock.
        """
        return self.mock_list_audits(self, *args, **kwargs)

    def list_auth_records(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.list_auth_records with MagicMock.
        """
        return self.mock_list_auth_records(self, *args, **kwargs)

    def replace_audit_destination(self, *args, **kwargs):
        """
        This method mocks the original api AuditsApi.replace_audit_destination with MagicMock.
        """
        return self.mock_replace_audit_destination(self, *args, **kwargs)

