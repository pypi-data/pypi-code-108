from typing import Optional

import numpy as np
import pandas as pd

from seeq.sdk import *
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy import _metadata
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.workbooks import _folder
from seeq.spy.workbooks import _pull
from seeq.spy.workbooks import _user
from seeq.spy.workbooks._item import Item
from seeq.spy.workbooks._workbook import Workbook


def push(workbooks, *, path=None, owner=None, label=None, datasource=None, datasource_map_folder=None,
         use_full_path=False, access_control=None, override_max_interp=False,
         include_inventory=True, scope_globals_to_workbook=False, refresh=True,
         errors='raise', quiet=False, status: Optional[Status] = None, session: Optional[Session] = None):
    """
    Pushes workbooks into Seeq using a list of Workbook object definitions.

    Parameters
    ----------
    workbooks : {Workbook, list[Workbook]}
        A Workbook object or list of Workbook objects to be pushed into Seeq.

    path : str, default None
        A '>>'-delimited folder path to create to contain the workbooks. Note
        that a further subfolder hierarchy will be created to preserve the
        relative paths that the folders were in when they were searched for
        and pulled. If you specify None, then the workbook will stay where
        it is (if it has already been pushed once). If you specify
        spy.workbooks.MY_FOLDER, it will be moved to the user's home folder.
        If you specify a folder ID directly, it will be pushed to that folder.

    owner : str, default None
        Determines the ownership of pushed workbooks and folders.

        By default, the current owner will be preserved. If the content doesn't
        exist yet, the logged-in user will be the owner.

        All other options require that the logged-in user is an admin:

        If spy.workbooks.ORIGINAL_OWNER, ownership is assigned according to the
        original owner of the pulled content.

        If spy.workbooks.FORCE_ME_AS_OWNER, existing content will be
        reassigned to the logged-in user.

        If a username or a user's Seeq ID is supplied, that user will be
        assigned as owner.

        You may need to supply an appropriate datasource map if the usernames
        are different between the original and the target servers.

    label : str
        A user-defined label that differentiates this push operation from
        others. By default, the label will be the logged-in user's username
        OR the username from the 'owner' argument so that push activity will
        generally be isolated by user. But you can override this with a label
        of your choosing.

    datasource : str, optional
        The name of the datasource within which to contain all the
        pushed items. By default, all pushed items will be contained in a "Seeq
        Data Lab" datasource. Do not create new datasources unless you really
        want to and you have permission from your administrator.

    datasource_map_folder : str, default None
        A folder containing Datasource_Map_Xxxx_Yyyy_Zzzz.json files that can
        provides a means to map stored items (i.e., those originating from
        external datasources like OSIsoft PI) from one server to another or
        from one datasource to another (i.e., for workbook swapping). A default
        set of datasource map files is created during a pull/save sequence, and
        you can copy these default files to a folder, alter them, and then
        specify the folder as this argument.

    use_full_path : bool, default False
        If True, the original full path for an item is reconstructed, as
        opposed to the path that is relative to the Path property supplied to
        the spy.workbooks.search() call that originally helped create these
        workbook definitions. Note that this full path will still be inside
        the folder specified by the 'path' argument, if supplied.

    access_control : str, default None
        Specifies how Access Control Lists should be treated, via the
        following keywords: add/replace,loose/strict

        If None, then no access control entries are pushed.
        If 'add', then existing access control entries will not be disturbed
          but new entries will be added.
        If 'replace', then existing access control entries will be removed
          and replaced with the entries from workbook definitions.

        If 'loose', then any unmapped users/groups from the workbook
          definitions will be silently ignored.
        If 'strict', then any unmapped users/groups will result in errors.

        Example: access_control='replace,loose'

    override_max_interp : bool, default False
        If True, then the Maximum Interpolation overrides from the source
        system will be written to the destination system.

    include_inventory : bool, default True
        If True, then all calculated items that are scoped to the workbook
        will be pushed as well.

    scope_globals_to_workbook : bool, default False
        If include_inventory=True and scope_globals_to_workbook=True, then
        all globally-scoped (aka "Available outside this analysis") items
        will be scoped to the workbook. False if you want to actually push
        these items to the global scope.

    refresh : bool, default True
        If True, then the Workbook objects that were supplied as input will
        be updated to be "fresh" from the server after the push. All
        identifiers will reflect the actual pushed IDs. Since refreshing
        takes time, you can set this to False if you don't plan to make
        further modifications to the Workbook objects or use the new IDs.

    errors : {'raise', 'catalog'}, default 'raise'
        If 'raise', any errors encountered will cause an exception. If
        'catalog', errors will be added to a 'Result' column in the status.df
        DataFrame (errors='catalog' must be combined with
        status=<Status object>).

    quiet : bool
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

    """
    _common.validate_argument_types([
        (workbooks, 'workbooks', (Workbook, list)),
        (path, 'path', str),
        (owner, 'owner', str),
        (label, 'label', str),
        (datasource, 'datasource', str),
        (datasource_map_folder, 'datasource_map_folder', str),
        (use_full_path, 'use_full_path', bool),
        (access_control, 'access_control', str),
        (override_max_interp, 'override_max_interp', bool),
        (include_inventory, 'include_inventory', bool),
        (scope_globals_to_workbook, 'scope_globals_to_workbook', bool),
        (refresh, 'refresh', bool),
        (errors, 'errors', str),
        (quiet, 'quiet', bool),
        (status, 'status', Status),
        (session, 'session', Session)
    ])

    status = Status.validate(status, quiet)
    session = Session.validate(session)
    _login.validate_login(session, status)

    _common.validate_errors_arg(errors)

    owner_identity = None
    if owner not in [None, _user.ORIGINAL_OWNER, _user.FORCE_ME_AS_OWNER]:
        owner_identity = _login.find_user(session, owner)
        owner = owner_identity.id

    status.update('Pushing workbooks', Status.RUNNING)

    item_map = dict()

    if not isinstance(workbooks, list):
        workbooks = [workbooks]

    # Make sure the datasource exists
    datasource_output = _metadata.create_datasource(session, datasource)

    # Sort such that Analyses are pushed before Topics, since the latter usually depends on the former
    remaining_workbooks = list()
    sorted_workbooks = sorted(list(workbooks), key=lambda w: w['Workbook Type'])
    status.df = pd.DataFrame(columns=['ID', 'Name', 'Type', 'Workbook Type', 'Count', 'Time', 'Result'])
    for index in range(len(sorted_workbooks)):  # type: int
        workbook = sorted_workbooks[index]
        remaining_workbooks.append((index, workbook))
        status.df.at[index, 'ID'] = workbook.id if workbook.id else np.nan
        status.df.at[index, 'Name'] = workbook.name
        status.df.at[index, 'Type'] = workbook.type
        status.df.at[index, 'Workbook Type'] = workbook['Workbook Type']
        status.df.at[index, 'Count'] = 0
        status.df.at[index, 'Time'] = 0
        status.df.at[index, 'Result'] = 'Queued'

    datasource_maps = None
    if datasource_map_folder:
        datasource_maps = Workbook.load_datasource_maps(datasource_map_folder)
        for datasource_map in datasource_maps:
            # Specifying Override = True causes the StoredItem push code to try to look up an item based on the map
            # instead of directly using the item's ID. This allows for pulling a workbook and then pushing it with a
            # datasource map to swap the items within it.
            datasource_map['Override'] = True

    folder_id = _create_folder_path_if_necessary(session, path)
    at_least_one_thing_pushed = False

    while len(remaining_workbooks) > 0:
        at_least_one_thing_pushed_this_iteration = False

        dependencies_not_found = list()
        for index, workbook in remaining_workbooks.copy():  # type: (int, Workbook)
            if not isinstance(workbook, Workbook):
                raise SPyRuntimeError('"workbooks" argument contains a non Workbook item: %s' % workbook)

            try:
                if label is None:
                    # If a label is not supplied, check to see if we should be automatically isolating by user.
                    isolate_by_user = False
                    if _common.get(workbook.definition, 'Isolate By User', default=False):
                        # Workbooks can be marked as 'Isolate By User' so they're not stepping on each other when
                        # they do spy.workbook.push(). All of the Example Exports are marked with "Isolate By User"
                        # equal to True.
                        isolate_by_user = True

                    if workbook.provenance == Item.CONSTRUCTOR:
                        # If a Workbook is constructed (and not persisted -- i.e., not pulled/loaded) then the best
                        # policy is to isolate such workbooks so that their Data IDs can't collide in the event that
                        # two users happen to name their workbooks the same.
                        isolate_by_user = True

                    if isolate_by_user:
                        label = owner_identity.username if owner_identity is not None else session.user.username

                status.reset_timer()

                status.current_df_index = index
                status.put('Count', 0)
                status.put('Time', 0)
                status.put('Result', 'Pushing')

                if datasource_maps is not None:
                    workbook.datasource_maps = datasource_maps

                workbook_folder_id = workbook.push_containing_folders(session, item_map, datasource_output,
                                                                      use_full_path, folder_id, owner, label,
                                                                      access_control)

                try:
                    workbook.push(owner=owner, folder_id=workbook_folder_id, item_map=item_map, label=label,
                                  datasource=datasource, access_control=access_control,
                                  override_max_interp=override_max_interp, include_inventory=include_inventory,
                                  scope_globals_to_workbook=scope_globals_to_workbook, status=status, session=session)

                    at_least_one_thing_pushed = True
                    at_least_one_thing_pushed_this_iteration = True
                    remaining_workbooks.remove((index, workbook))
                    status.put('Result', 'Success')

                    if len(workbook.item_push_errors) > 0:
                        raise SPyRuntimeError(workbook.item_push_errors_str)

                except SPyDependencyNotFound as e:
                    status.put('Count', 0)
                    status.put('Time', 0)
                    status.put('Result', f'Need dependency: {str(e)}')

                    dependencies_not_found.append(str(e))

            except BaseException as e:
                _common.raise_or_catalog(errors, status, e=e)

        if not at_least_one_thing_pushed_this_iteration:
            if errors == 'raise':
                raise SPyRuntimeError('Could not find the following dependencies:\n%s\n'
                                      'Therefore, could not import the following workbooks:\n%s\n' %
                                      ('\n'.join(dependencies_not_found),
                                       '\n'.join([str(workbook) for workbook in workbooks])))

            break

    for index in range(len(workbooks)):
        workbook = workbooks[index]
        status.update('[%s/%s] Fixing up workbook-to-workbook links: %s' %
                      (index + 1, len(workbooks), str(workbook)), Status.RUNNING)
        # If the workbook is a topic that has unresolved dependencies, the push will fail. We should have already
        # caught this when pushing the first time, so we can just continue here
        try:
            workbook.push_fixed_up_workbook_links(session, item_map, label, datasource_output)
        except SPyDependencyNotFound:
            continue

    if refresh and at_least_one_thing_pushed:
        pull_df = status.df.copy()
        pull_df.drop(columns=['ID'], inplace=True)
        pull_df.rename(columns={'Pushed Workbook ID': 'ID'}, inplace=True)
        new_workbooks = _pull.pull(pull_df, include_inventory=include_inventory,
                                   errors=errors, status=status.create_inner('Refresh Workbook'), session=session)
        for workbook in workbooks:
            new_workbook = [w for w in new_workbooks if w.id == item_map[workbook.id]][0]
            workbook.refresh_from(new_workbook, item_map)
            if folder_id is not None and folder_id != _common.PATH_ROOT:
                workbook['Search Folder ID'] = folder_id

    unique_results = status.df['Result'].drop_duplicates()
    if len(unique_results) > 1 or (len(unique_results) == 1 and unique_results.iloc[0] != 'Success'):
        status.update('Errors encountered, look at Result column in returned DataFrame', Status.FAILURE)
    else:
        status.update('Push successful', Status.SUCCESS)

    return status.df


def _create_folder_path_if_necessary(session: Session, path):
    if _common.is_guid(path):
        return path

    folders_api = FoldersApi(session.client)

    if path is None:
        return None

    path = path.strip()

    if not path:
        return None

    if path == _folder.MY_FOLDER:
        return folders_api.get_folder(folder_id='mine').id

    workbook_path = _common.path_string_to_list(path)

    parent_id = None
    folder_id = None
    folder_filter = 'owner'
    for i in range(0, len(workbook_path)):
        existing_content_id = None
        content_name = workbook_path[i]

        if content_name in [_folder.SHARED, _folder.ALL, _folder.USERS]:
            raise SPyRuntimeError(f'"path" argument cannot contain {content_name} folder')

        if content_name == _folder.CORPORATE:
            if not session.corporate_folder:
                raise SPyRuntimeError(f'Attempting to push to Corporate folder but user does not have access')

            parent_id = session.corporate_folder.id
            folder_id = session.corporate_folder.id
            folder_filter = 'corporate'
            continue

        if parent_id:
            folders = folders_api.get_folders(filter=folder_filter,
                                              folder_id=parent_id,
                                              limit=10000)  # type: WorkbenchItemOutputListV1
        else:
            folders = folders_api.get_folders(filter=folder_filter,
                                              limit=10000)  # type: WorkbenchItemOutputListV1

        for content in folders.content:  # type: WorkbenchSearchResultPreviewV1
            if content.type == 'Folder' and content_name == content.name:
                existing_content_id = content.id
                break

        if not existing_content_id:
            folder_input = FolderInputV1()
            folder_input.name = content_name
            folder_input.description = 'Created by Seeq Data Lab'
            folder_input.owner_id = session.user.id
            folder_input.parent_folder_id = parent_id
            folder_output = folders_api.create_folder(body=folder_input)  # type: FolderOutputV1
            existing_content_id = folder_output.id

        parent_id = existing_content_id
        folder_id = existing_content_id

    return folder_id
