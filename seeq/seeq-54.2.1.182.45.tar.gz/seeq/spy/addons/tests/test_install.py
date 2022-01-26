import pandas as pd
import pytest

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _login, Session
from seeq.spy import addons
from seeq.spy._errors import *
from seeq.spy.addons import _permissions
from seeq.spy.addons.tests import test_common as addons_test_common
from seeq.spy.tests import test_common
from seeq.spy.tests.test_common import Sessions


def setup_module():
    test_common.initialize_sessions()
    addons_test_common.enable_addon_tools(test_common.get_session(Sessions.admin), True)


def _create_testing_group():
    admin_session = test_common.get_session(Sessions.admin)
    user_groups_api = UserGroupsApi(admin_session.client)
    group_name = 'testers'

    # Note this code used to employ a read-then-write pattern where we would attempt to find the group and,
    # if not found, create it. This was vulnerable to a race condition when running tests in parallel: One test would
    # create the group in between the other test's find/create operations. Now we just try to create the group and if
    # that fails due to the group already existing, then find the group.

    group = None
    try:
        group = user_groups_api.create_user_group(body={"name": group_name})
    except ApiException as e:
        if e.status == 400:
            # This indicates that the group has already been created
            pass
        else:
            raise

    if group is None:
        group = _login.find_group(admin_session, group_name)

    return group


def _cleanup(name):
    admin_session = test_common.get_session(Sessions.admin)
    df = addons.search(pd.DataFrame([{'Name': f'{name}'}]), session=admin_session)
    if len(df) > 0:
        addons.uninstall(df, session=admin_session)


@pytest.mark.system
def test_addon_support():
    addons_test_common.test_addon_support(spy.session, 'install', dict())


def tool_names(session: Session):
    system_api = SystemApi(session.client)
    tools = system_api.get_add_on_tools().add_on_tools
    return [tool.name for tool in tools]


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_install_one_tool():
    items_api = ItemsApi(spy.session.client)

    new_name = "test_install_one_tool"
    my_tool = {"Name": new_name,
               "Description": "My new tool",
               "Target URL": "http://www.google.com",
               "Groups": ["Everyone"]}

    try:
        with pytest.raises(Exception):
            # This will cause "Only administrators may create add-on tools" exception
            addons.install(my_tool)

        admin_session = test_common.get_session(Sessions.admin)
        df = addons.install(my_tool, session=admin_session)
        assert items_api.get_item_and_all_properties(id=df['ID'].values[0])
        permissions = _permissions.get_addon_permissions(df['ID'].values[0], items_api)
        assert 'Everyone' in permissions['Groups']
        assert new_name in tool_names(admin_session)

        with pytest.raises(Exception):
            # This will cause "Only administrators may delete add-on tools" exception
            addons.uninstall(df)

    finally:
        _cleanup(new_name)


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_install_one_tool_with_existing_query_params():
    admin_session = test_common.get_session(Sessions.admin)
    items_api = ItemsApi(admin_session.client)

    new_name = "test_install_one_tool_with_existing_query_params"
    my_tool = {"Name": new_name,
               "Description": "My new tool",
               "Target URL": "http://www.google.com?previous=123",
               "Icon": "fa fa-icon"}

    try:
        df = addons.install(my_tool, include_workbook_parameters=True, session=admin_session)
        tool = items_api.get_item_and_all_properties(id=df['ID'].values[0])
        workbook_params = f'&workbookId={{workbookId}}&worksheetId={{worksheetId}}&workstepId={{' \
                          f'workstepId}}&seeqVersion={{seeqVersion}}'
        target_url = f"{my_tool['Target URL']}{workbook_params}"
        assert target_url == [x for x in tool.properties if x.name == 'Target URL'][0].value

    finally:
        _cleanup(new_name)


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_install_one_tool_with_workbook_params():
    admin_session = test_common.get_session(Sessions.admin)
    items_api = ItemsApi(admin_session.client)

    new_name = f"test_install_one_tool_with_workbook_params"
    my_tool = {"Name": new_name,
               "Description": "My new tool",
               "Target URL": "http://www.google.com?",
               "Icon": "fa fa-icon"}

    try:
        df = addons.install(my_tool, include_workbook_parameters=True, session=admin_session)
        tool = items_api.get_item_and_all_properties(id=df['ID'].values[0])
        workbook_params = f'workbookId={{workbookId}}&worksheetId={{worksheetId}}&workstepId={{' \
                          f'workstepId}}&seeqVersion={{seeqVersion}}'
        target_url = f"{my_tool['Target URL']}{workbook_params}"
        assert target_url == [x for x in tool.properties if x.name == 'Target URL'][0].value

    finally:
        _cleanup(new_name)


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_install_multiple_tools():
    admin_session = test_common.get_session(Sessions.admin)
    items_api = ItemsApi(admin_session.client)
    projects_api = ProjectsApi(admin_session.client)
    users_api = UsersApi(admin_session.client)

    user_id = users_api.get_me().id
    sdl_project1 = projects_api.create_project(body=dict(name='test project 1', ownerId=user_id))
    sdl_project2 = projects_api.create_project(body=dict(name='test project 1', ownerId=user_id))

    name = 'test_install_multiple_tools'
    new_tools = [
        {
            "Name": f'My {name}',
            "Description": "this is an awesome tool",
            "Target URL": f"http://www.my.seeq.com/data-lab/{sdl_project1.id}/apps/my_tool.ipynb",
            "Icon": "fa fa-bell"},
        {
            "Name": f'Your {name}',
            "Description": "this is an awesome tool",
            "Target URL": f"http://www.my.seeq.com/data-lab/{sdl_project2.id}/apps/tool2.ipynb",
            "Icon": "fa fa-bars"}]

    try:
        df = addons.install(new_tools, errors='raise', session=admin_session)
        for idd in df['ID'].values:
            assert items_api.get_item_and_all_properties(id=idd)

        for tool in new_tools:
            assert tool['Name'] in tool_names(admin_session)

    finally:
        _cleanup(f'*{name}')


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_update_tool_false():
    admin_session = test_common.get_session(Sessions.admin)
    items_api = ItemsApi(admin_session.client)

    name = "test_update_tool_false"
    my_tool = {"Name": name,
               "Description": "My new tool",
               "Target URL": "http://www.google.com",
               "Icon": "fa fa-icon"}

    try:
        df = addons.install(my_tool, update_tool=False, session=admin_session)
        assert items_api.get_item_and_all_properties(id=df['ID'].values[0])
        assert name in tool_names(admin_session)
        with pytest.raises(SPyException,
                           match=f'Add-on tool with name "{name}" already exists. '
                                 f'You can update the existing tool with `update_tool=True`'):
            addons.install(my_tool, update_tool=False, session=admin_session)

    finally:
        _cleanup(name)


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_update_tools_from_df():
    admin_session = test_common.get_session(Sessions.admin)
    projects_api = ProjectsApi(admin_session.client)
    users_api = UsersApi(admin_session.client)

    user_id = users_api.get_me().id
    sdl_project1 = projects_api.create_project(body=dict(name='test project 1', ownerId=user_id))
    sdl_project2 = projects_api.create_project(body=dict(name='test project 1', ownerId=user_id))

    name = 'test_update_tools_from_df'
    new_tools = [
        {
            "Name": f'My {name}',
            "Description": "this is an awesome tool",
            "Target URL": f"http://www.my.seeq.com/data-lab/{sdl_project1.id}/apps/my_tool.ipynb",
            "Icon": "fa fa-bell",
            "Link Type": "window"},
        {
            "Name": f'Your {name}',
            "Description": "this is an awesome tool",
            "Target URL": f"http://www.my.seeq.com/data-lab/{sdl_project2.id}/apps/tool2.ipynb",
            "Icon": "fa fa-bars",
            "Link Type": "window"}]

    try:
        df = addons.install(new_tools, session=admin_session)

        searched_tools = addons.search(df, session=admin_session)

        for _, tool in searched_tools.iterrows():
            assert tool['Link Type'] == 'window'

        searched_tools["Link Type"] = ['tab'] * len(searched_tools)
        addons.install(searched_tools, update_tool=True, session=admin_session)

        searched_tools = addons.search(df, session=admin_session)

        for _, tool in searched_tools.iterrows():
            assert tool['Link Type'] == 'tab'

    finally:
        _cleanup(f'*{name}')


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_change_permissions():
    admin_session = test_common.get_session(Sessions.admin)
    projects_api = ProjectsApi(admin_session.client)
    users_api = UsersApi(admin_session.client)
    items_api = ItemsApi(admin_session.client)
    group = _create_testing_group()

    user_id = users_api.get_me().id
    sdl_project1 = projects_api.create_project(body=dict(name='test project 1', ownerId=user_id))
    sdl_project2 = projects_api.create_project(body=dict(name='test project 1', ownerId=user_id))
    name = 'test_change_permissions'
    new_tools = [
        {
            "Name": f'My {name}',
            "Description": "this is an awesome tool",
            "Target URL": f"http://www.my.seeq.com/data-lab/{sdl_project1.id}/apps/my_tool.ipynb",
            "Icon": "fa fa-bell",
            "Link Type": "window",
            "Groups": ["testers"]},
        {
            "Name": f'Your {name}',
            "Description": "this is an awesome tool",
            "Target URL": f"http://www.my.seeq.com/data-lab/{sdl_project2.id}/apps/tool2.ipynb",
            "Icon": "fa fa-bars",
            "Link Type": "window",
            "Groups": ["testers"]}]

    try:
        addons.install(new_tools, session=admin_session)

        search_df = addons.search({"Name": f'My test_change_permissions'}, session=admin_session)

        # Pass only the ID to make sure it's not grabbing other properties from the search_df
        idd = search_df['ID'][0]

        # Remove group permissions
        addons.install(pd.Series({"ID": idd, "Groups": []}), update_permissions=True, update_tool=False,
                       session=admin_session)

        permissions = _permissions.get_addon_permissions(idd, items_api)
        assert len(permissions['Groups']) == 0
        assert len(permissions["Users"]) == 0

        addons.install({"ID": idd, "Groups": [group.name]}, update_permissions=True, session=admin_session)

    finally:
        _cleanup(f'*{name}')


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_update_tools_and_update_permissions_passing_id():
    _create_testing_group()

    projects_api = ProjectsApi(spy.session.client)
    users_api = UsersApi(spy.session.client)

    user_id = users_api.get_me().id
    sdl_project1 = projects_api.create_project(body=dict(name='test project 1', ownerId=user_id))
    sdl_project2 = projects_api.create_project(body=dict(name='test project 1', ownerId=user_id))

    name = 'test_update_tools_and_update_permissions_passing_id'
    new_tools = [
        {
            "Name": f'My {name}',
            "Description": "this is an awesome tool",
            "Target URL": f"http://www.my.seeq.com/data-lab/{sdl_project1.id}/apps/my_tool.ipynb",
            "Icon": "fa fa-bell",
            "Link Type": "window",
            "Groups": ["Everyone"]
        },
        {
            "Name": f'Your {name}',
            "Description": "this is an awesome tool",
            "Target URL": f"http://www.my.seeq.com/data-lab/{sdl_project2.id}/apps/tool2.ipynb",
            "Icon": "fa fa-bars",
            "Link Type": "window"}]

    admin_session = test_common.get_session(Sessions.admin)
    try:
        df = addons.install(new_tools, session=admin_session)

        searched_tools = addons.search(df)

        for _, tool in searched_tools.iterrows():
            assert tool['Link Type'] == 'window'

        searched_tools["Link Type"] = ['tab'] * len(searched_tools)
        searched_tools['Groups'] = [['testers']] * len(searched_tools)
        addons.install(searched_tools, update_tool=True, update_permissions=True, session=admin_session)

        searched_tools = addons.search(df)

        for _, tool in searched_tools.iterrows():
            assert tool['Link Type'] == 'tab'
            assert 'testers' in tool['Groups']
            assert 'Everyone' not in tool['Groups']

    finally:
        _cleanup(f'*{name}')


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_mix_update_tool_and_new_tool():
    admin_session = test_common.get_session(Sessions.admin)
    items_api = ItemsApi(admin_session.client)

    name = "test_mix_update_tool_and_new_tool"
    my_tool = {"Name": name,
               "Description": "an awesome tool",
               "Target URL": "http://www.google.com?",
               "Icon": "fa fa-icon"}

    try:
        df = addons.install(my_tool, include_workbook_parameters=True, update_tool=True, session=admin_session)
        previous_id = df['ID'].values[0]
        tool = items_api.get_item_and_all_properties(id=previous_id)
        assert my_tool['Description'] == [x for x in tool.properties if x.name == 'Description'][0].value

        new_install = [{"Name": name,
                        "Description": "an awesome tool updated",
                        "Target URL": "http://www.google.com?",
                        "Icon": "fa fa-icon"},
                       {"Name": f'New {name}',
                        "Description": "this is new",
                        "Target URL": "http://www.google.com?",
                        "Icon": "fa fa-icon"}]

        df = addons.install(new_install, include_workbook_parameters=True, update_tool=True, session=admin_session)
        tool = items_api.get_item_and_all_properties(id=previous_id)
        tool2 = items_api.get_item_and_all_properties(id=df['ID'][1])
        assert new_install[0]['Description'] == [x for x in tool.properties if x.name == 'Description'][0].value
        assert new_install[1]['Description'] == [x for x in tool2.properties if x.name == 'Description'][0].value
        assert len(df) == 2
        assert df['Result'][0] == 'Updated'
        assert df['Result'][1] == 'Installed'

    finally:
        _cleanup(f'*{name}')


# noinspection HttpUrlsUsage
@pytest.mark.system
def test_update_duplicated_tool():
    admin_session = test_common.get_session(Sessions.admin)
    system_api = SystemApi(admin_session.client)
    name = "test_update_duplicated_tool"

    new_tool_config = dict(
        name=name,
        description="duplicated test",
        iconClass='fa fa-bars',
        targetUrl=f'https://www.seeq.com',
        linkType="window",
        windowDetails="toolbar=0,height=600,width=600",
        sortKey="a",
        # need to cast to bool if coming from pandas as np.bool_
        reuseWindow=True,
    )

    try:
        tool1_id = system_api.create_add_on_tool(body=new_tool_config).id
        system_api.create_add_on_tool(body=new_tool_config)

        my_tool = {"Name": name,
                   "Description": "an awesome tool",
                   "Target URL": "http://www.google.com?",
                   "Icon": "fa fa-icon"}

        # addons.install fails to update if update_tool=False
        with pytest.raises(SPyException,
                           match=f'Add-on tool with name "{name}" already exists. '
                                 f'You can update the existing tool with `update_tool=True`'):
            addons.install(my_tool, include_workbook_parameters=True, update_tool=False, session=admin_session)

        # addons.install fails to update even with update_tool=True since there are two tools with the same name
        with pytest.raises(SPyException,
                           match=f'There exists 2 tools with the name "{name}". '
                                 f'You can supply the ID to avoid ambiguity and modify only the intended tool'):
            addons.install(my_tool, include_workbook_parameters=True, update_tool=True, session=admin_session)

        my_tool = {"ID": tool1_id,
                   "Name": name,
                   "Description": "an awesome tool",
                   "Target URL": "http://www.google.com?",
                   "Icon": "fa fa-icon"}

        # passing the ID resolves the ambiguity and allows the update
        df = addons.install(my_tool, include_workbook_parameters=True, update_tool=True, session=admin_session)

        assert len(df) == 1
        assert df['Result'][0] == 'Updated'

    finally:
        _cleanup(name)
