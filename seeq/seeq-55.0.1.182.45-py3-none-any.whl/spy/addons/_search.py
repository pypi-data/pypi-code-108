import copy
import types
from typing import Optional

import pandas as pd

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.addons import _common as _addons_common
from seeq.spy.addons import _permissions


# noinspection HttpUrlsUsage
def search(query, *, quiet=False, status=None, session: Optional[Session] = None):
    """
    Issues a query to the Seeq Server to retrieve metadata for Add-on tools.
    This metadata can be used to update or uninstall Add-on tools.

    Parameters
    ----------
    query : {dict, list, pd.DataFrame, pd.Series}
        A mapping of property / match-criteria pairs

        If you supply a dict or list of dicts, then the matching
        operations are "contains" (instead of "equal to").

        If you supply a DataFrame or a Series, then the matching
        operations are "equal to" (instead of "contains").

        'Name' field allows you to query all installed Add-on Tools by using
        the wildcard '*'.

        Available options are:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        ID                  The ID of the Add-on tool
        Name                The name of the Add-on tool
        Description         The description of the Add-on tool
        Target URL          The URL that the Add-on opens
        Icon                Name of the fontawesome icon class displayed on the
                            Add-on tool
        Link Type           Display characteristics of the Add-on tool. Either
                            "window", "tab" or None
        Window Details      Display characteristics used when linkType is set
                            to "window"
        Sort Key            Determines the order in which the Add-on Tools are
                            displayed in the tool panel
        Reuse Window        True or False.
        =================== ===================================================

    quiet : bool, default False
        If True, suppresses progress output. Note that when status is
        provided, the quiet setting of the Status object that is passed
        in takes precedent.

    status : spy.Status, optional
        If specified, the supplied Status object will be updated as the command
        progresses. It gets filled in with the same information you would see
        in Jupyter in the blue/green/red table below your code while the
        command is executed. The table itself is accessible as a DataFrame via
        the status.df property.

    session : spy.Session, optional
        If supplied, the Session object (and its Options) will be used to
        store the login session state. This is useful to log in to different
        Seeq servers at the same time or with different credentials.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with rows for each item found and columns for each
        property.

        Additionally, the following properties are stored on the "spy"
        attribute of the output DataFrame:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        func                A str value of 'spy.addons.search'
        kwargs              A dict with the values of the input parameters
                            passed to spy.addons.search to get the output
                            DataFrame
        status              A spy.Status object with the status of the
                            spy.addons.search call
        =================== ===================================================

    Examples
    --------
    Search for all the currently installed Add-on tools

    >>> search_results = spy.addons.search({'Name': '*'})

    To access the stored properties:
    >>> search_results.spy.kwargs
    >>> search_results.spy.status

    Search for an Add-on given its ID

    >>> search_results = spy.addons.search({"ID": "B540FF01-56B7-43AD-AE81-67AACB36C7F3"})

    Search for multiple Add-ons in the same spy.addons.search call:

    >>> search_results = spy.addons.search([{"Name": "Tool Name"}, {'Target URL': 'http://www.google.com'}])

    Search for multiple Add-ons using a pd.DataFrame

    >>> my_items = pd.DataFrame(
    >>>     {'Name': ['My Tool Name', 'Awesome Tool'],
    >>>      'Link Type': 'window'})
    >>> spy.addons.search(my_items)

    """

    input_args = _common.validate_argument_types([
        (query, 'query', (str, dict, list, pd.DataFrame, pd.Series)),
        (quiet, 'quiet', bool),
        (status, 'status', Status),
        (session, 'session', Session)
    ])

    status = Status.validate(status, quiet)
    session = Session.validate(session)
    _login.validate_login(session, status)
    _addons_common.verify_addons_support(session)

    try:
        return _search(session, query, quiet=quiet, status=status, input_args=input_args)

    except KeyboardInterrupt:
        status.update('Search canceled', Status.CANCELED)


def _search(session: Session, query_, *, quiet=False, status=None, input_args=None):
    status = Status.validate(status, quiet)

    system_api = SystemApi(session.client)
    items_api = ItemsApi(session.client)
    tools = system_api.get_add_on_tools().add_on_tools
    if len(tools) == 0:
        status.update(
            f'There are zero Add-on tools installed',
            Status.SUCCESS)
        output_df = pd.DataFrame()
        add_properties_to_result(input_args, status, output_df)
        return output_df
    tool_dicts = [x.to_dict() for x in tools]
    for tool in tool_dicts:
        # Need a try/except here because of CRAB-23267
        # The issue was supposedly fixed in R52.0.0 but we encountered the issue here again only for v52.
        # Once R52 is phased out we can potentially removed the except
        try:
            permissions = _permissions.get_addon_permissions(tool['id'], items_api)
        except ApiException:
            permissions = {"Groups": ["needs admin rights to display"], "Users": ["needs admin rights to display"]}
        tool['groups'] = permissions['Groups']
        tool['users'] = permissions['Users']
    tools_df = pd.DataFrame(tool_dicts)

    query_copy = copy.deepcopy(query_)  # To avoid modifying the original object passed by the user

    if isinstance(query_copy, pd.DataFrame):
        queries = query_copy.to_dict(orient='records')
        comparison = '=='
    elif isinstance(query_copy, pd.Series):
        queries = [query_copy.to_dict()]
        comparison = '=='
    elif isinstance(query_copy, list):
        queries = query_copy
        comparison = '~='
    else:
        queries = [query_copy]
        comparison = '~='

    status.df = pd.DataFrame(queries)
    status.df['Time'] = 0
    status.df['Count'] = 0
    status.df['Result'] = 'Queued'
    status.update('Initializing', Status.RUNNING)

    results = []
    all_props = {'id': 'ID',
                 'name': 'Name',
                 'description': 'Description',
                 'target_url': 'Target URL',
                 'icon_class': 'Icon',
                 'link_type': 'Link Type',
                 'sort_key': 'Sort Key',
                 'reuse_window': 'Reuse Window',
                 'groups': "Groups",
                 'users': "Users",
                 'type': 'Type',
                 'is_archived': 'Archived',
                 'status_message': 'Status Message',
                 'window_details': 'Window Details'
                 }

    output_column_order = list(all_props.values())

    allowed_properties = ['ID', 'Name', 'Description', 'Target URL', 'Icon', 'Link Type', 'Sort Key',
                          'Reuse Window', 'Window Details']
    allowed_properties = {v: k for k, v in all_props.items() if v in allowed_properties}

    disallowed_properties = list()
    for status_index, current_query in enumerate(queries):
        for key, value in current_query.items():
            if key not in allowed_properties.keys():
                disallowed_properties.append(key)

        for key in disallowed_properties:
            if key in current_query:
                del current_query[key]

    if len(set(disallowed_properties)) > 0:
        disallowed_properties_str = '", "'.join(list(set(disallowed_properties)))
        message = f'The following properties are not indexed and will be ignored: "{disallowed_properties_str}"'
        status.warn(message)

    for status_index, current_query in enumerate(queries):
        timer = _common.timer_start()

        if not current_query:
            status.df.at[status_index, 'Time'] = _common.timer_elapsed(timer)
            status.df.at[status_index, 'Count'] = 0
            status.df.at[status_index, 'Result'] = 'Success'
            continue

        df_current_query = tools_df.copy()
        for prop in current_query.keys():
            # If ID is passed, then short-circuit the current query and return just the ID
            if 'ID' in current_query:
                query_str = f"id=='{current_query['ID']}'"
                df_current_query = tools_df.query(query_str)
                status.df.at[status_index, 'Count'] = len(df_current_query)
                break

            else:
                if prop == 'Name' and current_query['Name'] == "*":
                    # If "*" is passed, then keep the current list (all tools if no other props are passed)
                    status.df.at[status_index, 'Count'] = len(df_current_query)
                else:
                    if _common.present(current_query, prop):
                        query_str = _regex_from_query(current_query[prop].strip(), contains=(comparison == '~='))
                        df_current_query = df_current_query[
                            df_current_query[allowed_properties[prop]].str.contains(query_str, regex=True)]
                        status.df.at[status_index, 'Count'] = len(df_current_query)

        status.df.at[status_index, 'Time'] = _common.timer_elapsed(timer)
        status.df.at[status_index, 'Result'] = 'Success'
        results.extend(df_current_query.to_dict('records'))

    status.update('Query successful', Status.SUCCESS)
    output_df = pd.DataFrame(results)
    output_df.rename(columns=all_props, inplace=True)
    if not output_df.empty:
        output_df = output_df[output_column_order]
        duplicate_series = output_df['ID'].value_counts()
        number_of_duplicates = duplicate_series.sum() - len(duplicate_series)
        if number_of_duplicates > 0:
            output_df.drop_duplicates('ID', ignore_index=True, inplace=True)
            status.update(
                f'Query successful - Dropped {number_of_duplicates} duplicate{"s" if number_of_duplicates > 1 else ""}',
                Status.SUCCESS)

    add_properties_to_result(input_args, status, output_df)

    return output_df


def _regex_from_query(query_fragment, contains=True):
    regex = _common.regex_from_query_fragment(query_fragment, contains)
    if not contains:
        regex = f"^{regex}$"
    return regex


def add_properties_to_result(input_args, status, output_df):
    output_df_properties = types.SimpleNamespace(
        func='spy.addons.search',
        kwargs=input_args,
        status=status)

    _common.put_properties_on_df(output_df, output_df_properties)
