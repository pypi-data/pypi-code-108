import pandas as pd
import pytest

from seeq.spy import addons
from seeq.spy.addons.tests import test_common as addons_test_common
from seeq.spy.tests import test_common
from seeq.spy.tests.test_common import Sessions


def setup_module():
    test_common.initialize_sessions()
    addons_test_common.enable_addon_tools(test_common.get_session(Sessions.admin), True)


@pytest.mark.system
def test_addon_support():
    admin_session = test_common.get_session(Sessions.admin)
    addons_test_common.test_addon_support(admin_session, 'uninstall', pd.DataFrame())


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_uninstall_tools():
    admin_session = test_common.get_session(Sessions.admin)
    unique_name_suffix = str(pd.to_datetime("today"))
    my_tools = [{"Name": f'test tool 1_{unique_name_suffix}',
                 "Description": "test tool 1",
                 "Target URL": "http://www.google.com",
                 "Icon": "fa fa-icon",
                 "Link Type": "tab"},
                {"Name": f'test tool 2_{unique_name_suffix}',
                 "Description": "test tool 2",
                 "Target URL": "http://www.seeq.com",
                 "Icon": "fa fa-icon"}]
    df_tools = addons.install(my_tools, session=admin_session)
    search_results = addons.search(df_tools, session=admin_session)

    assert len(search_results) == 2
    addons.uninstall(search_results, session=admin_session)
    search_results = addons.search(df_tools, session=admin_session)

    assert search_results.empty
