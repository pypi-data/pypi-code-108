import pytest

from seeq import spy
from seeq.sdk import *
from seeq.spy import _common
from seeq.spy.tests import test_common
from seeq.spy.tests.test_common import Sessions
from seeq.spy.workbooks import Analysis
from seeq.spy.workbooks.tests import test_load


def setup_module():
    test_common.initialize_sessions()


@pytest.mark.system
def test_non_recursive():
    workbooks = test_load.load_example_export()
    spy.workbooks.push(workbooks, path='Non-Recursive Import', errors='catalog', label='test_non_recursive')
    workbooks_df = spy.workbooks.search({
        'Path': 'Non-Recursive*'
    })
    assert len(workbooks_df) == 2

    workbooks_df = spy.workbooks.search({
        'Path': 'Non-Recursive*',
        'Name': '*Analysis'
    })
    assert len(workbooks_df) == 1
    assert workbooks_df.iloc[0]['Name'] == 'Example Analysis'
    assert workbooks_df.iloc[0]['Type'] == 'Workbook'
    assert workbooks_df.iloc[0]['Workbook Type'] == 'Analysis'

    workbooks_df = spy.workbooks.search({
        'Path': 'Non-Recursive*',
        'Workbook Type': 'Topic'
    })
    assert len(workbooks_df) == 1
    assert workbooks_df.iloc[0]['Name'] == 'Example Topic'
    assert workbooks_df.iloc[0]['Type'] == 'Workbook'
    assert workbooks_df.iloc[0]['Workbook Type'] == 'Topic'


@pytest.mark.system
def test_recursive():
    workbooks = test_load.load_example_export()
    spy.workbooks.push(workbooks, path='Recursive Import >> Another Folder Level', errors='catalog',
                       label='test_recursive')
    workbooks_df = spy.workbooks.search({
        'Path': 'Recursive I?port'
    })
    assert len(workbooks_df) == 1
    assert workbooks_df.iloc[0]['Name'] == 'Another Folder Level'
    assert workbooks_df.iloc[0]['Type'] == 'Folder'

    workbooks_df = spy.workbooks.search({
        'Path': r'/Recursive\sImport/',
        'Name': '*Analysis'
    }, recursive=True)
    assert len(workbooks_df) == 1
    assert workbooks_df.iloc[0]['Name'] == 'Example Analysis'
    assert workbooks_df.iloc[0]['Type'] == 'Workbook'
    assert workbooks_df.iloc[0]['Workbook Type'] == 'Analysis'

    workbooks_df = spy.workbooks.search({
        'Path': r'/^Recursive.*/',
        'Workbook Type': 'Topic'
    }, recursive=True)
    assert len(workbooks_df) == 1
    assert workbooks_df.iloc[0]['Name'] == 'Example Topic'
    assert workbooks_df.iloc[0]['Type'] == 'Workbook'
    assert workbooks_df.iloc[0]['Workbook Type'] == 'Topic'


@pytest.mark.system
def test_archived():
    archived_workbook = spy.workbooks.Analysis({'Name': 'An Archived Workbook'})
    archived_workbook.worksheet('Only Worksheet')
    not_archived_workbook = spy.workbooks.Analysis({'Name': 'A Not Archived Workbook'})
    not_archived_workbook.worksheet('Only Worksheet')
    spy.workbooks.push([archived_workbook, not_archived_workbook], path='test_archived')
    items_api = ItemsApi(spy.session.client)
    items_api.set_property(id=archived_workbook.id, property_name='Archived', body=PropertyInputV1(value=True))
    try:
        search_df = spy.workbooks.search({'Path': 'test_archived'}, include_archived=True)
        assert len(search_df) == 2
        assert 'An Archived Workbook' in search_df['Name'].tolist()
        assert 'A Not Archived Workbook' in search_df['Name'].tolist()
        search_df = spy.workbooks.search({'Path': 'test_archived'}, include_archived=False)
        assert len(search_df) == 1
        assert search_df.iloc[0]['Name'] == 'A Not Archived Workbook'
    finally:
        # Unarchive it so we can run this test over and over
        items_api.set_property(id=archived_workbook.id, property_name='Archived', body=PropertyInputV1(value=False))


@pytest.mark.system
def test_content_filters():
    workbook_name = f'test_sections_{_common.new_placeholder_guid()}'
    workbook = Analysis(workbook_name)
    workbook.worksheet('The Worksheet')

    def _assert_location(_location, _session):
        # Asserts that workbook appears under a certain content_filter but not others

        for _content_filter in ['owner', 'public', 'shared', 'corporate']:
            _search_df = spy.workbooks.search(
                {'Name': workbook_name}, content_filter=_content_filter, recursive=False, session=_session)
            assert len(_search_df) == (1 if _location == _content_filter else 0)

    # First push to Corporate drive
    spy.workbooks.push(workbook, path=spy.workbooks.CORPORATE)
    _assert_location('corporate', spy.session)

    # Now un-publish from Corporate drive back to user folder
    spy.workbooks.push(workbook, path=spy.PATH_ROOT)
    _assert_location('owner', spy.session)

    # Use admin to make sure it doesn't show up in any (non-ALL) searches
    admin_session = test_common.get_session(Sessions.admin)
    _assert_location('none', admin_session)

    # Make sure it shows up in ALL search
    search_df = spy.workbooks.search({'Name': workbook_name}, content_filter='all', recursive=False,
                                     session=admin_session)
    assert len(search_df) == 1

    # Now share the workbook with the admin so it would appear under Shared on the Home Screen
    items_api = ItemsApi(admin_session.client)
    admin_user = test_common.get_user(admin_session, test_common.ADMIN_USER_NAME)
    acl_output = items_api.add_access_control_entry(
        id=workbook.id,
        body=AceInputV1(identity_id=admin_user.id,
                        permissions=PermissionsV1(read=True)))
    _assert_location('shared', admin_session)

    # Now un-share it with admin and share it with Everyone so it appears as Public
    for ace_id in [ace.id for ace in acl_output.entries if ace.identity.username == 'admin@seeq.com']:
        items_api.remove_access_control_entry(id=workbook.id, ace_id=ace_id)

    everyone_group = test_common.get_group(admin_session, 'Everyone')
    items_api.add_access_control_entry(
        id=workbook.id,
        body=AceInputV1(identity_id=everyone_group.id,
                        permissions=PermissionsV1(read=True)))
    _assert_location('public', admin_session)


@pytest.mark.system
def test_root_directories():
    workbook_name = f'test_sections_{_common.new_placeholder_guid()}'
    workbook = Analysis(workbook_name)
    workbook.worksheet('The Worksheet')
    folders_to_test = [spy.workbooks.ALL, spy.workbooks.CORPORATE, spy.workbooks.MY_FOLDER, spy.workbooks.SHARED,
                       spy.workbooks.USERS]

    def _assert_root_dir(_location, _content_filter):
        # Asserts that when the path contains the root directory, the workbook is found in the correct root directory
        for _root_dir in folders_to_test:
            _search_df = spy.workbooks.search({'Name': workbook_name, 'Path': f'{_root_dir}'},
                                              recursive=False, content_filter=_content_filter)
            if _root_dir == spy.workbooks.ALL:
                expected_length = 1
            elif _location == _root_dir:
                expected_length = 1
            else:
                expected_length = 0

            assert len(_search_df) == expected_length

    # push to corporate, search with different root directories and matching and non-matching content_filters
    spy.workbooks.push(workbook, path=spy.workbooks.CORPORATE)
    _assert_root_dir(spy.workbooks.CORPORATE, 'corporate')
    _assert_root_dir(spy.workbooks.CORPORATE, 'owner')

    # push to user directory, search with different root directories and matching and non-matching content_filters
    spy.workbooks.push(workbook, path=spy.workbooks.MY_FOLDER)
    _assert_root_dir(spy.workbooks.MY_FOLDER, 'owner')
    _assert_root_dir(spy.workbooks.MY_FOLDER, 'public')
    _assert_root_dir(spy.workbooks.MY_FOLDER, 'corporate')
