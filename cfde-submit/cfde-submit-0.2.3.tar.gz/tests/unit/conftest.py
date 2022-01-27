from unittest.mock import Mock, PropertyMock
import pytest
import fair_research_login
import globus_sdk

from cfde_submit import CONFIG, version, validation, globus_http, bdbag_utils
import cfde_submit

# Maximum output logging!
CONFIG['LOGGING']['handlers']['console']['class'] = 'logging.StreamHandler'
CONFIG['LOGGING']['handlers']['console']['level'] = 'DEBUG'


@pytest.fixture(autouse=True)
def mock_login(monkeypatch):
    """Unit tests should never need to call login() or logout(), as doing so
    would use real developer credentials"""
    monkeypatch.setattr(fair_research_login.NativeClient, "login", Mock())
    monkeypatch.setattr(fair_research_login.NativeClient, "logout", Mock())
    return fair_research_login.NativeClient


@pytest.fixture(autouse=True)
def mock_remote_config(monkeypatch):
    """Ensure no actual remote fetching of config stuff is used
    For the day you want to test fetching remote configs:
    https://stackoverflow.com/questions/38748257/disable-autouse-fixtures-on-specific-pytest-marks
    """
    catalog_keys = ["flow_id", "success_step", "failure_step", "error_step", "cfde_ep_id"]
    mock_catalog = {
        "CATALOGS": {
            "prod": "prod",
            "staging": "staging",
            "dev": "dev"
        },
        "FLOWS": {
            "prod": {k: f"prod_{k}" for k in catalog_keys},
            "staging": {k: f"staging_{k}" for k in catalog_keys},
            "dev": {k: f"dev_{k}" for k in catalog_keys},
        },
        "MIN_VERSION": version.__version__
    }
    for service in mock_catalog["FLOWS"].keys():
        mock_catalog["FLOWS"][service]["cfde_ep_path"] = f'/CFDE/data/{service}/'
        mock_catalog["FLOWS"][service]["cfde_ep_url"] = f'https://{service}' \
                                                        f'-gcs-inst.data.globus.org'
    remote_config = PropertyMock(return_value=mock_catalog)
    monkeypatch.setattr(cfde_submit.CfdeClient, 'remote_config', remote_config)
    return remote_config


@pytest.fixture(autouse=True)
def mock_flows_client(monkeypatch):
    """Ensure there are no calls out to the Globus Automate Client"""
    monkeypatch.setattr(cfde_submit.CfdeClient, 'flow_client', PropertyMock())
    return cfde_submit.CfdeClient.flow_client


@pytest.fixture(autouse=True)
def mock_gcp_uninstalled(monkeypatch):
    """Mock the state of the user's machine where Globus Connect Personal is
    NOT installed. autouse=True due to this being the more likely state of the
    user's machine."""
    gcp_inst = Mock()
    gcp_inst.endpoint_id = None
    monkeypatch.setattr(globus_sdk, 'LocalGlobusConnectPersonal', Mock(return_value=gcp_inst))
    return gcp_inst


@pytest.fixture
def mock_gcp_installed(mock_gcp_uninstalled):
    mock_gcp_uninstalled.endpoint_id = 'local_gcp_endpoint_id'
    return mock_gcp_uninstalled


@pytest.fixture
def mock_upload(monkeypatch):
    monkeypatch.setattr(globus_http, 'upload', Mock())
    return globus_http.upload


@pytest.fixture
def mock_get_bag(monkeypatch):
    """Simply returns the path passed in, and does no error checking on any local bags"""
    def mock_get_bag(bag_path, *args, **kwargs):
        return bag_path
    monkeypatch.setattr(bdbag_utils, 'get_bag', mock_get_bag)
    return bdbag_utils.get_bag


@pytest.fixture
def mock_validation(monkeypatch):
    monkeypatch.setattr(validation, 'validate_user_submission', Mock())
    return validation.validate_user_submission


@pytest.fixture
def mock_dcc_check(monkeypatch):
    monkeypatch.setattr(cfde_submit.CfdeClient, "valid_dcc", Mock())
    return cfde_submit.CfdeClient.valid_dcc


@pytest.fixture
def logged_out(monkeypatch):
    load = Mock(side_effect=fair_research_login.LoadError())
    monkeypatch.setattr(fair_research_login.NativeClient, "load_tokens_by_scope", load)
    return fair_research_login.NativeClient


@pytest.fixture
def logged_in(monkeypatch, mock_remote_config):
    scopes = [
        'https://auth.globus.org/scopes/dev_cfde_ep_id/https',
        'https://auth.globus.org/scopes/staging_cfde_ep_id/https',
        'https://auth.globus.org/scopes/prod_cfde_ep_id/https',
        'urn:globus:auth:scope:transfer.api.globus.org:all',
    ] + CONFIG["ALL_SCOPES"]
    mock_tokens = {
        scope: dict(access_token=f"{scope}_access_token")
        for scope in scopes
    }
    load = Mock(return_value=mock_tokens)
    monkeypatch.setattr(fair_research_login.NativeClient, "load_tokens_by_scope", load)
    return fair_research_login.NativeClient


@pytest.fixture
def mock_globus_api_error(monkeypatch):
    class MockGlobusAPIError(Exception):
        pass
    monkeypatch.setattr(globus_sdk, 'GlobusAPIError', MockGlobusAPIError)
    return globus_sdk.GlobusAPIError


@pytest.fixture
def mock_globus_sdk(monkeypatch):
    setattr(globus_sdk.TransferClient, "operation_ls", PropertyMock())
    return globus_sdk
