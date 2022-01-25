import pandas as pd
import pytest

from seeq import spy
from seeq.sdk import *
from seeq.spy import addons, Session
from seeq.spy.addons.tests import test_common as addons_test_common
from seeq.spy.tests import test_common
from seeq.spy.tests.test_common import Sessions


def setup_module():
    test_common.initialize_sessions()
    addons_test_common.enable_addon_tools(test_common.get_session(Sessions.admin), True)


# noinspection HttpUrlsUsage
def _create_test_tools(session: Session, suffix_=''):
    my_tools = [{"Name": f'test tool 1_{suffix_}',
                 "Description": f"test tool 1{suffix_}",
                 "Target URL": "http://www.google.com",
                 "Icon": "fa fa-icon",
                 "Link Type": "tab",
                 "Users": [session.user.username]},
                {"Name": f'test tool 2_{suffix_}',
                 "Description": f"test tool 2{suffix_}",
                 "Target URL": "http://www.seeq.com",
                 "Icon": "fa fa-icon",
                 "Users": [session.user.username]
                 }]
    # searching for tools doesn't require admin access but creating tools does
    tools = addons.install(my_tools, session=test_common.get_session(Sessions.admin))
    return tools


def _uninstall_test_tools(ids):
    for idd in ids:
        system_api = SystemApi(test_common.get_session(Sessions.admin).client)
        system_api.delete_add_on_tool(id=idd)


@pytest.mark.system
def test_addon_support():
    addons_test_common.test_addon_support(spy.session, 'search', dict())


@pytest.mark.system
def test_search_df_metadata():
    query = {'Name': '*'}
    search_results = addons.search(query)

    assert isinstance(search_results.spy.status.df, pd.DataFrame)
    assert search_results.spy.kwargs['query'] == query


@pytest.mark.system
def test_search_with_wildcard_plus_another_prop():
    unique_name_suffix = str(pd.to_datetime("today"))
    session = test_common.get_session(Sessions.nonadmin)
    df_tools = _create_test_tools(session, suffix_=unique_name_suffix)

    query = {'Name': '*', "Description": f"2{unique_name_suffix}"}
    search_results = addons.search(query, session=session)

    assert len(search_results) == 1
    # clean up
    _uninstall_test_tools(df_tools['ID'].values)


@pytest.mark.system
def test_search_with_wildcard_plus_id():
    unique_name_suffix = str(pd.to_datetime("today"))
    session = test_common.get_session(Sessions.nonadmin)
    df_tools = _create_test_tools(session, suffix_=unique_name_suffix)

    query = {'Name': '*', "ID": df_tools['ID'].values[0]}
    search_results = addons.search(query, session=session)

    assert len(search_results) == 1

    # clean up
    _uninstall_test_tools(df_tools['ID'].values)


@pytest.mark.system
def test_search_by_id():
    unique_name_suffix = str(pd.to_datetime("today"))
    session = test_common.get_session(Sessions.nonadmin)
    df_tools = _create_test_tools(session, suffix_=unique_name_suffix)
    idd = df_tools['ID'][0]
    search_results = addons.search({"ID": idd}, session=session)
    assert len(search_results) == 1
    # clean up
    _uninstall_test_tools(df_tools['ID'].values)


@pytest.mark.system
def test_search_with_df():
    unique_name_suffix = str(pd.to_datetime("today"))
    session = test_common.get_session(Sessions.nonadmin)
    df_tools = _create_test_tools(session, suffix_=unique_name_suffix)
    my_items = pd.DataFrame(
        {'Name': [f'test tool 1_{unique_name_suffix}', f'test tool 2_{unique_name_suffix}'],
         'Link Type': 'window'})
    search_results = addons.search(my_items, session=session)
    assert len(search_results) == 1
    assert search_results['Link Type'][0] == 'window'

    # clean up
    _uninstall_test_tools(df_tools['ID'].values)


@pytest.mark.system
def test_search_with_multiple_props():
    unique_name_suffix = str(pd.to_datetime("today"))
    session = test_common.get_session(Sessions.nonadmin)
    df_tools = _create_test_tools(session, suffix_=unique_name_suffix)

    search = addons.search({"Name": "test tool", "Description": "test tool"}, session=session)
    assert len(search) >= 2

    search_results_no_match = addons.search(
        pd.DataFrame([{"Name": f'test tool', "Description": "test tool"}]))
    search_results_match = addons.search(pd.DataFrame([{"Name": f'test tool 1_{unique_name_suffix}',
                                                        "Description": f"test tool 1{unique_name_suffix}"},
                                                       {"Name": f'test tool 2_{unique_name_suffix}',
                                                        "Description": f"test tool 2{unique_name_suffix}"}]),
                                         session=session)
    assert len(search_results_match) - len(search_results_no_match) == 2

    # clean up
    _uninstall_test_tools(df_tools['ID'].values)
