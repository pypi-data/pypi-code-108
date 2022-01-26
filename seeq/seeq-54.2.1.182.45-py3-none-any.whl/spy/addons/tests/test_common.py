import mock
import pytest

from seeq import spy
from seeq.sdk import *
from seeq.spy import _login, Session
from seeq.spy import addons
from seeq.spy._errors import *
from seeq.spy.addons import _common as _addons_common

ERROR_52 = f"Seeq R52 versions before R52.1.5 do not support spy.addons"
ERROR_53 = f"Seeq R53 versions before R53.0.2 do not support spy.addons"


def enable_addon_tools(session: Session, value):
    system_api = SystemApi(session.client)
    config_option_input = ConfigurationOptionInputV1(path='Features/AddOnTools/Enabled', value=value)
    system_api.set_configuration_options(body=ConfigurationInputV1([config_option_input]))


def test_addon_support(session: Session, addon_function, input_args):
    # only testing for the current major version. Otherwise, _login.validate will complain of different
    # SPy-SeeqServer versions
    major_version, *_ = _login.get_server_version_tuple(spy.session)
    error = ERROR_52 if major_version == 52 else ERROR_53 if major_version == 53 else None
    if major_version <= 53:
        with mock.patch.object(_login, 'get_server_version_tuple', return_value=(major_version, 0, 0)):
            with pytest.raises(SPyException, match=error):
                getattr(addons, addon_function)(input_args)


@pytest.mark.unit
def test_verify_addons_support():
    with mock.patch.object(_login, 'get_server_version_tuple', return_value=(52, 0, 0)):
        with pytest.raises(SPyException, match=ERROR_52):
            _addons_common.verify_addons_support(spy.session)

    with mock.patch.object(_login, 'get_server_version_tuple', return_value=(52, 1, 4)):
        with pytest.raises(SPyException, match=ERROR_52):
            _addons_common.verify_addons_support(spy.session)

    with mock.patch.object(_login, 'get_server_version_tuple', return_value=(52, 1, 5)):
        _addons_common.verify_addons_support(spy.session)

    with mock.patch.object(_login, 'get_server_version_tuple', return_value=(52, 2, 0)):
        _addons_common.verify_addons_support(spy.session)

    with mock.patch.object(_login, 'get_server_version_tuple', return_value=(53, 0, 0)):
        with pytest.raises(SPyException, match=ERROR_53):
            _addons_common.verify_addons_support(spy.session)

    with mock.patch.object(_login, 'get_server_version_tuple', return_value=(53, 0, 1)):
        with pytest.raises(SPyException, match=ERROR_53):
            _addons_common.verify_addons_support(spy.session)

    with mock.patch.object(_login, 'get_server_version_tuple', return_value=(53, 0, 2)):
        _addons_common.verify_addons_support(spy.session)

    with mock.patch.object(_login, 'get_server_version_tuple', return_value=(53, 1, 0)):
        _addons_common.verify_addons_support(spy.session)

    with mock.patch.object(_login, 'get_server_version_tuple', return_value=(54, 1, 0)):
        _addons_common.verify_addons_support(spy.session)
