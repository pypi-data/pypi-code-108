import os
import textwrap
import time
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict

import pandas as pd
import pytest

from seeq import spy
from seeq.base import util
from seeq.sdk import *
from seeq.spy import Session
from seeq.spy import _common, _metadata
from seeq.spy.workbooks import Analysis

ADMIN_USER_NAME = 'admin@seeq.com'
ADMIN_PASSWORD = 'myadminpassword'

NON_ADMIN_NAME = 'non_admin'
NON_ADMIN_LAST_NAME = 'tester'
NON_ADMIN_USERNAME = f'{NON_ADMIN_NAME}.{NON_ADMIN_LAST_NAME}@seeq.com'
NON_ADMIN_PASSWORD = 'mynonadminpassword'


class Sessions(Enum):
    agent = 'agent'
    admin = 'admin'
    nonadmin = 'nonadmin'
    ren = 'ren'
    stimpy = 'stimpy'
    test_path_search_pagination = 'test_path_search_pagination'
    test_search_pagination = 'test_search_pagination'
    test_order_by_page_size = 'test_order_by_page_size'
    test_pull_signal_with_grid = 'test_pull_signal_with_grid'
    test_pull_condition_as_capsules = 'test_pull_condition_as_capsules'
    test_push_from_csv = 'test_push_from_csv'


@dataclass
class Credential:
    username: Optional[str] = None
    password: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


SESSION_CREDENTIALS = {
    Sessions.agent: Credential(username='agent_api_key', password=None, first_name=None, last_name=None),
    Sessions.admin: Credential(username='admin@seeq.com', password='myadminpassword', first_name=None, last_name=None),
    Sessions.nonadmin: Credential(username='non_admin.tester@seeq.com', password='mynonadminpassword',
                                  first_name='non_admin', last_name='tester'),
    Sessions.ren: Credential(username='ren', password='ren12345',
                             first_name='Ren', last_name='Hoek'),
    Sessions.stimpy: Credential(username='stimpy', password='stimpy12',
                                first_name='Stimpson J.', last_name='tester')
}

sessions: Optional[Dict[Sessions, Session]] = None


def get_session(session_name):
    global sessions
    if sessions is None:
        add_all_credentials()
        util.os_lock('seeq_spy_system_tests', _initialize_seeq_database, timeout=60)
        log_in_all_test_users()
        set_retry_timeout_for_all_sessions(600)  # Set high to mitigate CRAB-28592
        wait_for_example_data(spy.session)

    return sessions[session_name]


def set_retry_timeout_for_all_sessions(timeout):
    for session in sessions.values():
        session.options.retry_timeout_in_seconds = timeout


def log_in_default_user(url=None):
    agent_credential = SESSION_CREDENTIALS[Sessions.agent]

    # this will be the default agent_api_key user which is a non-auto complete identity
    key_path = os.path.join(get_test_data_folder(), 'keys', 'agent.key')
    with open(key_path, "r") as f:
        SESSION_CREDENTIALS[Sessions.agent].username, SESSION_CREDENTIALS[Sessions.agent].password = \
            f.read().splitlines()

    spy.login(agent_credential.username, agent_credential.password, url=url, session=spy.session)


def log_out_default_user():
    spy.logout(session=spy.session)


def _initialize_seeq_database():
    global sessions
    sessions = dict()

    log_in_default_user()
    sessions[Sessions.agent] = spy.session

    create_admin_user(spy.session)
    admin_session = Session()
    spy.login(SESSION_CREDENTIALS[Sessions.admin].username, SESSION_CREDENTIALS[Sessions.admin].password,
              session=admin_session)
    sessions[Sessions.admin] = admin_session

    # It is important to create the Seeq Data Lab datasource while we're inside the os_lock() call, otherwise there
    # is a race condition where it can be created twice which kills all the tests.
    _metadata.create_datasource(spy.session)

    add_all_test_users()


def add_all_credentials():
    global sessions
    for session_name in Sessions:
        if session_name not in SESSION_CREDENTIALS:
            SESSION_CREDENTIALS[session_name] = \
                Credential(username=session_name.value, password=f'{session_name.value}12345678',
                           first_name=session_name.value, last_name=session_name.value)


def add_all_test_users():
    global sessions
    for session_name in Sessions:
        if session_name in [Sessions.agent, Sessions.admin]:
            continue

        credential = SESSION_CREDENTIALS[session_name]

        add_normal_user(sessions[Sessions.admin],
                        credential.first_name, credential.last_name, credential.username, credential.password)

        user_session = Session()
        spy.login(credential.username, credential.password, session=user_session)
        sessions[session_name] = user_session


def log_in_all_test_users():
    global sessions
    for session_name in Sessions:
        if session_name in [Sessions.agent, Sessions.admin]:
            continue

        credential = SESSION_CREDENTIALS[session_name]

        user_session = Session()
        spy.login(credential.username, credential.password, session=user_session)
        sessions[session_name] = user_session


def initialize_sessions():
    """
    This function should be called in the setup_module() function for all system tests that require Seeq Server to be
    running.
    """
    check_if_server_is_running()
    get_session(Sessions.agent)


def check_if_server_is_running():
    try:
        system_api = SystemApi(ApiClient(host='http://localhost:34216/api'))
        system_api.get_server_status()
    except BaseException as e:
        raise RuntimeError("Seeq Server is not responding. If you're running this from IntelliJ, make sure you "
                           "ran 'sq run -c' from the top-level crab folder first, and wait for Seeq Server to "
                           f"boot up fully. Here's the exception that system_api.get_server_status() returned:\n{e}")


def get_user(session: Session, username) -> Optional[UserOutputV1]:
    users_api = UsersApi(session.client)
    user_output_list = users_api.get_users()
    for user in user_output_list.users:  # type: UserOutputV1
        if user.username == username:
            return user

    return None


def get_group(session: Session, group_name) -> Optional[IdentityPreviewV1]:
    user_groups_api = UserGroupsApi(session.client)
    user_groups_output_list = user_groups_api.get_user_groups()
    for group in user_groups_output_list.items:  # type: IdentityPreviewV1
        if group.name == group_name:
            return group

    return None


def add_normal_user(session: Session, first_name, last_name, username, password) -> UserOutputV1:
    user = get_user(session, username)
    if user:
        return user

    users_api = UsersApi(session.client)
    return users_api.create_user(body=UserInputV1(
        first_name=first_name,
        last_name=last_name,
        email=username,
        username=username,
        password=password
    ))


def create_admin_user(session: Session):
    user = get_user(session, ADMIN_USER_NAME)
    if user:
        return user

    admin_reset_properties = os.path.join(get_test_data_folder(), 'configuration', 'admin_reset.properties')
    with open(admin_reset_properties, 'w') as f:
        f.write(textwrap.dedent(f"""
                email = {ADMIN_USER_NAME}
                password = {ADMIN_PASSWORD}
            """))

    timeout = time.time()
    while True:
        if time.time() - timeout > 30:
            raise Exception(f'Timed out creating admin user {ADMIN_USER_NAME}')

        if get_user(session, ADMIN_USER_NAME):
            break

        time.sleep(0.01)


def get_test_data_folder():
    return os.path.normpath(
        os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', 'sq-run-data-dir'))


def wait_for(boolean_function):
    start = time.time()
    while True:
        if boolean_function():
            break

        if time.time() - start > 240:
            return False

        time.sleep(1.0)

    return True


def wait_for_example_data(session: Session):
    start = time.time()
    while True:
        if is_example_data_indexed(session):
            return

        if time.time() - start > 240:
            raise Exception("Timed out waiting for Example Data to finish indexing")

        time.sleep(1.0)


def is_example_data_indexed(session: Session):
    # noinspection PyBroadException
    try:
        agents_api = AgentsApi(session.client)
        agent_status = agents_api.get_agent_status()
        for agents in agent_status:
            if 'JVM Agent' in agents.id:
                if agents.status != 'CONNECTED':
                    return False

                for connection in agents.connections:
                    if 'Example Data' in connection.name and \
                            connection.status == 'CONNECTED' and \
                            connection.sync_status == 'SYNC_SUCCESS':
                        return True

    except BaseException:
        return False

    return False


def create_worksheet_for_url_tests(name):
    search_results = spy.search({
        'Name': 'Temperature',
        'Path': 'Example >> Cooling Tower 1 >> Area A'
    }, workbook=spy.GLOBALS_ONLY)

    display_items = pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Temperature Minus 5',
        'Formula': '$a - 5',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }, {
        'Type': 'Condition',
        'Name': 'Cold',
        'Formula': '$a.validValues().valueSearch(isLessThan(80))',
        'Formula Parameters': {
            '$a': search_results.iloc[0]
        }
    }, {
        'Type': 'Scalar',
        'Name': 'Constant',
        'Formula': '5',
    }])

    push_df = spy.push(metadata=display_items, workbook=None)

    workbook = Analysis({
        'Name': name
    })

    worksheet = workbook.worksheet('search from URL')
    worksheet.display_range = {
        'Start': '2019-01-01T00:00Z',
        'End': '2019-01-02T00:00Z'
    }
    worksheet.display_items = push_df

    spy.workbooks.push(workbook)

    return workbook


@pytest.mark.unit
def test_escape_regex():
    assert _common.escape_regex(r'mydata\trees') == r'mydata\\trees'
    assert _common.escape_regex(r'Hello There') == r'Hello There'
    assert _common.escape_regex(r'Hello\ There') == r'Hello\\ There'
    assert _common.escape_regex(r' Hello There ') == r' Hello There '
    assert _common.escape_regex('\\ Hello   There  \\') == '\\\\ Hello   There  \\\\'
    assert _common.escape_regex(r'\ Hello <>! There') == r'\\ Hello <>! There'


@pytest.mark.unit
def test_is_guid():
    assert _common.is_guid('2b17adfd-3308-4c03-bdfb-bf4419bf7b3a') is True
    assert _common.is_guid('test 2b17adfd-3308-4c03-bdfb-bf4419bf7b3a') is False
    assert _common.is_guid('2b17adfd-3308-4c03-bdfb-bf4419bf7b3a test') is False
    assert _common.is_guid('2G17adfd-3308-4c03-bdfb-bf4419bf7b3a') is False
    assert _common.is_guid('2b17adfd-3308-4c03-bdfb') is False
    assert _common.is_guid('Hello world') is False
    assert _common.is_guid('') is False
    # noinspection PyTypeChecker
    assert _common.is_guid(123) is False


@pytest.mark.unit
def test_string_to_formula_literal():
    with pytest.raises(ValueError):
        _common.string_to_formula_literal(1)

    assert _common.string_to_formula_literal("mark") == "'mark'"
    assert _common.string_to_formula_literal("'''") == r"'\'\'\''"
    assert _common.string_to_formula_literal(r"\path\to\thing") == r"'\\path\\to\\thing'"
