from unittest.mock import Mock, patch

import pytest

from anyscale.controllers.base_controller import BaseController


@pytest.mark.parametrize("initialize_auth_api_client", [True, False])
def test_api_client_authenticated(
    initialize_auth_api_client: bool,
    base_mock_api_client,
    base_mock_anyscale_api_client,
):
    """
    Test a controller that inherits from BaseController has api_client and anyscale_api_client correctly
    populated if initialize_auth_api_client==True and raises an error when these fields
    are called if initialize_auth_api_client==False.
    """

    class Controller(BaseController):
        def test_call_api_client(self,):
            return self.api_client

        def test_call_anyscale_api_client(self,):
            return self.anyscale_api_client

    mock_get_auth_api_client = Mock(
        return_value=Mock(
            api_client=base_mock_api_client,
            anyscale_api_client=base_mock_anyscale_api_client,
        )
    )
    with patch.multiple(
        "anyscale.controllers.base_controller",
        get_auth_api_client=mock_get_auth_api_client,
    ):
        controller = Controller(initialize_auth_api_client=initialize_auth_api_client)
    if not initialize_auth_api_client:
        mock_get_auth_api_client.assert_not_called()
        with pytest.raises(Exception):
            controller.test_call_api_client()
        with pytest.raises(Exception):
            controller.test_call_anyscale_api_client()
    else:
        mock_get_auth_api_client.assert_called_once_with()
        assert controller.api_client == base_mock_api_client
        assert controller.anyscale_api_client == base_mock_anyscale_api_client
