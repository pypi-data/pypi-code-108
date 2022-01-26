from unittest.mock import MagicMock

class MessagesApiMock:

    def __init__(self):
        self.mock_create_message = MagicMock()
        self.mock_create_user_message = MagicMock()
        self.mock_delete_message_endpoint = MagicMock()
        self.mock_get_message_endpoint = MagicMock()
        self.mock_list_message_endpoints = MagicMock()
        self.mock_list_messages_config = MagicMock()
        self.mock_replace_message_endpoint = MagicMock()
        self.mock_update_message_endpoint = MagicMock()

    def create_message(self, *args, **kwargs):
        """
        This method mocks the original api MessagesApi.create_message with MagicMock.
        """
        return self.mock_create_message(self, *args, **kwargs)

    def create_user_message(self, *args, **kwargs):
        """
        This method mocks the original api MessagesApi.create_user_message with MagicMock.
        """
        return self.mock_create_user_message(self, *args, **kwargs)

    def delete_message_endpoint(self, *args, **kwargs):
        """
        This method mocks the original api MessagesApi.delete_message_endpoint with MagicMock.
        """
        return self.mock_delete_message_endpoint(self, *args, **kwargs)

    def get_message_endpoint(self, *args, **kwargs):
        """
        This method mocks the original api MessagesApi.get_message_endpoint with MagicMock.
        """
        return self.mock_get_message_endpoint(self, *args, **kwargs)

    def list_message_endpoints(self, *args, **kwargs):
        """
        This method mocks the original api MessagesApi.list_message_endpoints with MagicMock.
        """
        return self.mock_list_message_endpoints(self, *args, **kwargs)

    def list_messages_config(self, *args, **kwargs):
        """
        This method mocks the original api MessagesApi.list_messages_config with MagicMock.
        """
        return self.mock_list_messages_config(self, *args, **kwargs)

    def replace_message_endpoint(self, *args, **kwargs):
        """
        This method mocks the original api MessagesApi.replace_message_endpoint with MagicMock.
        """
        return self.mock_replace_message_endpoint(self, *args, **kwargs)

    def update_message_endpoint(self, *args, **kwargs):
        """
        This method mocks the original api MessagesApi.update_message_endpoint with MagicMock.
        """
        return self.mock_update_message_endpoint(self, *args, **kwargs)

