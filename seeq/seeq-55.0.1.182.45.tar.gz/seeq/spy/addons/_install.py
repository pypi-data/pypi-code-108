import copy
import re
import types
from typing import Optional
from urllib.parse import urlparse

import pandas as pd

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy import _url
from seeq.spy import addons
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.addons import _common as _addons_common
from seeq.spy.addons import _permissions


# noinspection HttpUrlsUsage
def install(tool, *, include_workbook_parameters=True, update_tool=False, update_permissions=False, errors='raise',
            quiet=False, status=None, session: Optional[Session] = None):
    """
    Installs or updates Add-on tool(s) in Seeq Workbench.
    Installing Add-on tools requires administrator access.

    Parameters
    ----------
    tool: {dict, list, pd.DataFrame, pd.Series}

        =================== ===================================================
        Property            Description
        =================== ===================================================
        Name                Required. The name of the Add-on tool (shown in
                            green text in the Add-on Tool card).

        Description         Required. The description of the Add-on tool (shown
                            in black text underneath the Name in the tool card).
                            Long descriptions will wrap to the next line and
                            increase the height of the Add-on Tool button.

        Target URL          Required.The URL that the Add-on will open. This
                            can be any website but most commonly a Seeq
                            Data Lab Notebook in Appmode. In order to get the
                            Target URL for a Seeq Data Lab Notebook, open the
                            desired Notebook and copy the URL. In normal mode,
                            the URL contains "/notebooks/" right after the
                            project ID. If you want the notebook to be opened
                            in Appmode, replace "/notebooks/" for "/apps/" in
                            the URL.
                            For example:
                            https://my.seeq.com/data-lab/<id>/apps/TEST.ipynb

        Icon                Optional. Name of the fontawesome icon class to be
                            displayed on the tool card. Defaults to
                            "fa fa-minus". Potential Font Awesome
                            icons can be found at the website
                            https://fontawesome.com/v4.7.0/icons/ and take the
                            form of "fa fa-<icon>" Be sure to include the
                            standalone "fa" in addition to the icon name.

        Link Type           Optional. Sets the display characteristics.
                            Defaults to "window".
                            Options are one of the following:
                                "window" - display in a new window. After the
                                           windows is opened, the user is
                                           responsible for subsequent managing
                                           of window placement.
                                "tab" - display in a new tab of the current
                                        browser window.
                                "none" - make a GET request to the URL but do
                                         not open a window or tab. Although
                                         supported, its use is expected to be
                                         rare. It should generally be avoided
                                         because it gives the tool card a
                                         non-standard button-like behavior.

        Window Details      Optional if Link Type is "window". Sets display
                            characteristics used when Link Type is set to
                            "window". Options are available at
                            https://developer.mozilla.org/en-US/docs/Web/API/Window/open#Window_features.
                            For example:
                            "toolbar=0,height=600,width=600"

        Sort Key            Optional. A string, typically a single character
                            letter. Determines the order in which the Add-on
                            Tools are displayed in the tool panel. The Add-on
                            Tools panel sorts the list of add-ons by this key
                            to determine ordering.

        Reuse Window        Optional. Defaults to False. If True, sets focus
                            to existing window if already opened. Otherwise,
                            open a new window. If False, a new window is opened
                            each time the tool card is clicked. This parameter
                            is only valid when Link Type is set to "window".

        Groups              Optional. List of the Seeq groups that have
                            permission to access the Add-on tool. If the
                            Add-on Tool Target URL is a Data Lab Notebook, then
                            any permissions set on the Add-on Tool will also be
                            added to the target Data Lab Project as users are
                            required to have at least write permissions on the
                            Data Lab Project to run the Notebook. Passing an
                            empty list will remove permissions to the tool for
                            all groups (without modifying permissions to the
                            Target URL). If the tool exists, set
                            update_permissions to True to overwrite the
                            previous Groups permissions. If the tool exists
                            and update_permissions is False, then permissions
                            will not update.

        Users               Optional. List of the Seeq users by username that
                            have permission to access the Add-on tool. To figure
                            out a username, go to the Users tab of the
                            Administration page, click "edit" for the user you
                            want to figure out their username, and get the
                            username from the dialog window that opens. If the
                            Add-on Tool Target URL is a Data Lab Notebook, then
                            any permissions set on the Add-on Tool will also
                            be added to the target Project as users
                            are required to have at least write permissions on
                            the Data Lab Project to run the Notebook. Passing an
                            empty list will remove permissions to the tool for
                            all users (without modifying permissions to the
                            Target URL). If the tool exists, set
                            update_permissions to True to overwrite the
                            previous Users permissions. If the tool exists
                            and update_permissions is False, then permissions
                            will not update.

        ID                  Optional. The ID of an existing Add-on tool. Only
                            needed if you want to update an already installed
                            Add-on tool or its permissions. update_tool or
                            update_permissions must be set to True if you
                            want to update an existing tool.
        =================== ===================================================

    include_workbook_parameters: bool, default True
        If True, the workbookId, worksheetId, workstepId, and/or
        seeqVersion are passed from the launched workbook through the URL as
        query parameters after the “.ipynb?”.
        For example:
        https://my.seeq.com/data-lab/<id>/apps/TEST.ipynb?workbookId={workbookId}&worksheetId={
        worksheetId}&workstepId={workstepId}&seeqVersion={seeqVersion}

    update_tool: bool, default False
        False will prevent an existing Add-on tool to be updated.
        True will update an existing Add-on tool. You must supply the ID of
        the tool(s) that you want to update.

    update_permissions: bool, default False
        False will prevent changing the current permissions on an existing
        Add-on tool and its Target URL.
        True will modify the current permissions on an existing Add-on tool as
        well as its Target URL. You must supply the ID of the tool(s) that you
        want to update its (their) permissions.

    errors : {'raise', 'catalog'}, default 'raise'
        If 'raise', any errors encountered will cause an exception. If
        'catalog', errors will be added to a 'Result' column in the status.df
        DataFrame.

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

    Notes
    -----
        Setting the Target URL to a non-appmode Data Lab project should be
        avoided. Non-appmode Data Lab projects would get their own container but
        technical limitations dictate that each container accesses the same
        files on a shared volume. This results in unwanted interactions, save
        notifications, and a last-save-wins behavior.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the metadata of the Add-on tools pushed, along with
        any errors and statistics about the operation.

        Additionally, the following properties are stored on the "spy"
        attribute of the output DataFrame:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        func                A str value of 'spy.addons.install'
        kwargs              A dict with the values of the input parameters
                            passed to spy.addons.install to get the output
                            DataFrame
        status              A spy.Status object with the status of the
                            spy.addons.install call
        =================== ===================================================

    Examples
    --------
    Install a new Add-on tool
    >>> my_new_tool = {
    >>>     "Name": 'My New Tool',
    >>>     "Description": "this is an awesome tool",
    >>>     "Target URL": "http://www.my.seeq.com/data-lab/8FB008FF-ECF0-4837-B3D4-7FCBB49CC108/apps/my_tool.ipynb",
    >>>     "Groups": ['My Seeq Group']}

    >>> df_installed = spy.addons.install(my_new_tool)

    If the tool already existed and you want to update it
    >>> df_installed = spy.addons.install(my_new_tool, update_tool=True)

    To installed multiple tools at once:
    >>> new_tools = [
    >>>     {
    >>>         "Name": 'My New Tool',
    >>>         "Description": "this is an awesome tool",
    >>>         "Target URL": "http://www.my.seeq.com/data-lab/8FB008FF-ECF0-4837-B3D4-7FCBB49CC108/apps/my_tool.ipynb",
    >>>         "Icon": "fa fa-bell",
    >>>         "Groups": ['My Seeq Group']},
    >>>     {
    >>>         "Name": 'Your New Tool',
    >>>         "Description": "this is an awesome tool",
    >>>         "Target URL": "http://www.my.seeq.com/data-lab/F4DS345D-23DS-2344-SVSE-345234TSDF52/apps/tool2.ipynb",
    >>>         "Icon": "fa fa-bars",
    >>>         "Groups": ['Everyone']}]

    >>> df_installed = spy.addons.install(new_tools)

    Or set the properties in a pd.DataFrame (useful when modifying existing tools by manipulating the pd.DataFrame
    from spy.addons.search):

    >>> searched_tools = spy.addons.search({"Link Type": "window"})
    >>> searched_tools["Link Type"] = ['tab'] * len(searched_tools)
    >>> df_installed = spy.addons.install(searched_tools,update_tool=True)

    To change group permissions:
    >>> searched_tools = spy.addons.search({"Name": "My New Tool"})
    >>> searched_tools["Groups"] = [['Everyone']] * len(searched_tools)
    >>> df_installed = spy.addons.install(searched_tools,update_permissions=True)

    To change user permissions
    >>> searched_tools = spy.addons.search({"Name": "My New Tool"})
    >>> searched_tools["Users"] = [['user@my.seeq.com']] * len(searched_tools)
    >>> df_installed = spy.addons.install(searched_tools,update_permissions=True)

    """

    input_args = _common.validate_argument_types([
        (tool, 'tool', (str, dict, list, pd.DataFrame, pd.Series)),
        (include_workbook_parameters, 'include_workbook_parameters', bool),
        (update_tool, "update_tool", bool),
        (update_permissions, "update_permissions", bool),
        (errors, 'errors', str),
        (quiet, 'quiet', bool),
        (status, 'status', Status),
        (session, 'session', Session)
    ])

    status = Status.validate(status, quiet)
    session = Session.validate(session)
    _login.validate_login(session, status)
    _addons_common.verify_addons_support(session)

    try:
        return _install(session, tool, include_workbook_parameters=include_workbook_parameters,
                        update_tool=update_tool,
                        update_permissions=update_permissions, errors=errors, quiet=quiet, status=status,
                        input_args=input_args)

    except KeyboardInterrupt:
        status.update('Add-on installation canceled', Status.CANCELED)


def _install(session: Session, tool, *, include_workbook_parameters=True, update_tool=False, update_permissions=False,
             errors='raise', quiet=False, status=None, input_args=None):
    status = Status.validate(status, quiet)
    tool_copy = copy.deepcopy(tool)  # To avoid modifying the original object passed by the user
    items_api = ItemsApi(session.client)
    system_api = SystemApi(session.client)

    if isinstance(tool_copy, pd.DataFrame):
        tools = tool_copy.to_dict(orient='records')
    elif isinstance(tool_copy, pd.Series):
        tools = [tool_copy.to_dict()]
    elif isinstance(tool_copy, list):
        tools = tool_copy
    else:
        tools = [tool_copy]

    for _tool in tools:
        tool_types = []
        for k, v in _tool.items():
            if k == "Reuse Window":
                tool_types.append((v, k, bool))
            elif k in ['Groups', 'Users']:
                tool_types.append((v, k, list))
                if isinstance(v, list):
                    tool_types.extend([(x, str(x), str) for x in v])
            elif k in ['Name', 'Description', 'Target URL', 'Icon', 'Link Type', 'Window Details', 'Sort Key', 'ID']:
                tool_types.append((v, k, str))
                if k == 'ID':
                    if not _common.is_guid(v):
                        raise SPyValueError(f'The ID "{v}" is malformed')
            elif k in ['Effective Permissions', 'Type', 'Archived', 'Status Message']:
                pass  # Ignore these keys since they might be coming from spy.addons.search
            else:
                raise SPyValueError(f"Property {k} is not a valid option for the `tool` parameter")

        _common.validate_argument_types(tool_types)

    defaults = {'Icon': 'fa fa-minus',
                'Link Type': 'window',
                'Sort Key': 'a',
                'Reuse Window': False,
                'Window Details': ''}

    required_props = {"Name", "Description", "Target URL"}
    tools_old = system_api.get_add_on_tools().add_on_tools

    status.df = pd.DataFrame()
    status.df['ID'] = ''
    status.df['Name'] = ''
    status.df['Target URL'] = ''
    status.df['Time'] = 0
    status.df['Result'] = 'Queued'
    status.update('Installing', Status.RUNNING)

    for status_idx, _tool in enumerate(tools):
        timer = _common.timer_start()
        tool_id = None

        if update_tool or update_permissions:
            status.update(f"Updating Add-on tool", Status.RUNNING)
            if 'ID' not in _tool.keys() and 'Name' not in _tool.keys():
                message = f"Either the Name or the ID must be supplied when update_tool is True"
                _common.raise_or_catalog(errors, status=status, exception_type=SPyException, index=status_idx,
                                         message=message)
                continue

            if 'ID' in _tool.keys():
                tool_id = _tool['ID']

            if 'ID' not in _tool.keys():
                tools_with_same_name = [x for x in tools_old if x.name == _tool['Name']]
                if len(tools_with_same_name) > 1:
                    message = f'There exists {len(tools_with_same_name)} tools with the name "{_tool["Name"]}". ' \
                              f'You can supply the ID to avoid ambiguity and modify only the intended tool'
                    _common.raise_or_catalog(errors, status=status, exception_type=SPyException, index=status_idx,
                                             message=message)
                elif len(tools_with_same_name) == 1:
                    tool_id = tools_with_same_name[0].id

            if tool_id is not None:
                tool_record = addons.search({"ID": tool_id}, quiet=True, session=session).to_dict('records')
                if not tool_record:
                    message = f'A tool with ID "{tool_id}" does not exist'
                    _common.raise_or_catalog(errors, status=status, exception_type=SPyException, index=status_idx,
                                             message=message)
                tool_old = tool_record[0]
                # Update the properties set by the user
                old_permissions = _permissions.get_addon_permissions(tool_id, items_api)
                tool_old['Groups'] = old_permissions['Groups']
                tool_old['Users'] = old_permissions['Users']
                for k in tool_old.keys():
                    if k not in _tool:
                        _tool[k] = tool_old[k]

        if tool_id is None:
            status.update('Installing Add-on', Status.RUNNING)
            if not required_props.issubset(_tool.keys()):
                addendum = ''
                if _tool.get('ID') is not None:
                    addendum = "Consider setting `update_tool=True` if your intention is to update only certain " \
                               "properties of an existing the tool."
                message = f"The properties {required_props} are required. Got properties {set(_tool.keys())} for tool" \
                          f" {status_idx}. {addendum}"
                _common.raise_or_catalog(errors, status=status, exception_type=SPyException, index=status_idx,
                                         message=message)
                continue
            # Use defaults for properties not set by the user
            if 'Icon' not in _tool.keys():
                _tool['Icon'] = defaults['Icon']

            if 'Link Type' not in _tool.keys():
                _tool['Link Type'] = defaults['Link Type']

            if 'Window Details' not in _tool.keys():
                _tool['Window Details'] = defaults['Window Details']

            if "Sort Key" not in _tool.keys():
                _tool['Sort Key'] = defaults['Sort Key']

            if "Reuse Window" not in _tool.keys():
                _tool['Reuse Window'] = defaults['Reuse Window']

            if 'ID' not in _tool.keys():
                _tool['ID'] = None

        for prop in ['Groups', 'Users']:
            if prop not in _tool.keys():
                _tool[prop] = []

        parsed_url = urlparse(_tool['Target URL'])
        target_url = parsed_url.geturl()

        datalab_project_id = _url.get_data_lab_project_id_from_url(target_url)
        if datalab_project_id is None:
            status.warn(
                f'It looks like the target URL for tool "{_tool["Name"]}" is not a Seeq Data Lab project. This is '
                f'typically not recommended. Make sure this is indeed your intent')

        query_params = parsed_url.query
        if include_workbook_parameters:
            workbook_params = '&workbookId={workbookId}&worksheetId={worksheetId}&workstepId={workstepId}' \
                              '&seeqVersion={seeqVersion}'

            if not re.search(workbook_params[1:], query_params):
                query_params += workbook_params
            query_params = query_params[1:] if query_params[0] == '&' else query_params

        else:
            # In case the workbook query parameters exists but user passes include_workbook_parameters=False
            for params in ['workbookId={workbookId}', 'worksheetId={worksheetId}', 'workstepId={workstepId}',
                           'seeqVersion={seeqVersion}']:
                query_params = query_params.replace(params, '')
                query_params = query_params.replace('&&', '&')
            if query_params:
                query_params = query_params[1:] if query_params[0] == '&' else query_params
            if query_params:
                query_params = query_params[:-1] if query_params[-1] == '&' else query_params

        new_tool_config = dict(
            name=_tool['Name'],
            description=_tool['Description'],
            iconClass=_tool['Icon'],
            targetUrl=f'{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}?{query_params}',
            linkType=_tool['Link Type'],
            windowDetails=_tool['Window Details'],
            sortKey=_tool['Sort Key'],
            # need to cast to bool if coming from pandas as np.bool_
            reuseWindow=True if _tool['Reuse Window'] else False,
            permissions=dict(groups=_tool['Groups'],
                             users=_tool['Users'])
        )

        status.df.at[status_idx, 'Name'] = new_tool_config['name']
        status.df.at[status_idx, 'Target URL'] = new_tool_config['targetUrl']

        if not update_tool and update_permissions and _tool.get('ID'):
            # We came this far for this check since we still need the target URL and permissions default checks
            status.df.at[status_idx, 'ID'] = _tool['ID']
            status.df.at[status_idx, 'Time'] = _common.timer_elapsed(timer)
            set_permissions(session, new_tool_config, _tool['ID'])
            status.df.at[status_idx, 'Result'] = 'Updated permissions'

        else:
            new_id = None
            try:
                new_id = _install_or_update_tool(session, new_tool_config, update_tool=update_tool, tool_id=_tool['ID'])
                if update_permissions or _tool['ID'] is None:
                    set_permissions(session, new_tool_config, new_id)
                status.df.at[status_idx, 'ID'] = new_id
                status.df.at[status_idx, 'Time'] = _common.timer_elapsed(timer)
                status.df.at[status_idx, 'Result'] = f"{'Updated' if _tool.get('ID') else 'Installed'}"
            except (ApiException, AssertionError, SPyValueError, SPyRuntimeError) as e:
                if new_id is not None and _tool['ID'] is None:
                    # We should get here only if there was a NEW tool that failed to be created
                    system_api.delete_add_on_tool(id=new_id)
                status.df.at[status_idx, 'Time'] = _common.timer_elapsed(timer)
                _common.raise_or_catalog(errors, status=status, index=status_idx, exception_type=SPyException,
                                         message=e)

    status.update(f'Add-on tool{"s" if len(tools) > 1 else ""} installation successful', Status.SUCCESS)

    install_result_df = status.df.copy()
    push_df_properties = types.SimpleNamespace(
        func='spy.addons.install',
        kwargs=input_args,
        status=status)

    _common.put_properties_on_df(install_result_df, push_df_properties)

    return install_result_df


def _install_or_update_tool(session: Session, new_tool_config, update_tool, tool_id):
    system_api = SystemApi(session.client)
    tools = system_api.get_add_on_tools().add_on_tools

    # If the tool is in the list
    tool_names = [tool.name for tool in tools]
    if new_tool_config["name"] in tool_names:
        if not update_tool or tool_id is None:
            message = f'Add-on tool with name "{new_tool_config["name"]}" already exists. You can update the ' \
                      f'existing tool with `update_tool=True`'
            raise SPyRuntimeError(message)

    tool = new_tool_config.copy()
    tool.pop("permissions")
    if tool_id is not None:
        # Update tool
        system_api.update_add_on_tool(id=tool_id, body=tool)
    else:
        # Create add-on tool
        tool_id = system_api.create_add_on_tool(body=tool).id

    return tool_id


def set_permissions(session: Session, new_tool_config, tool_id):
    items_api = ItemsApi(session.client)

    try:
        data_lab_project_id = _url.get_data_lab_project_id_from_url(new_tool_config["targetUrl"])
    except SPyRuntimeError:
        data_lab_project_id = None

    groups = new_tool_config["permissions"]["groups"]
    users = new_tool_config["permissions"]["users"]

    # revoke previous permissions
    _permissions.remove_addon_permissions(tool_id, "UserGroup", items_api)

    for group_name in groups:
        group = _login.find_group(session, group_name, exact_match=True)
        if group:
            # assign group permissions to add-on tool and data lab project
            _permissions.set_addon_permissions(group.id, tool_id, items_api)
            if data_lab_project_id:
                _permissions.datalab_permissions(group.id, data_lab_project_id, items_api)

    # revoke previous permissions
    _permissions.remove_addon_permissions(tool_id, "User", items_api)
    for user_name in users:
        _user = _login.find_user(session, user_name, exact_match=True)
        if _user:
            # assign user permissions to add-on tool and data lab project
            _permissions.set_addon_permissions(_user.id, tool_id, items_api)
            if data_lab_project_id:
                _permissions.datalab_permissions(_user.id, data_lab_project_id, items_api)
