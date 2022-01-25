from typing import Optional

import numpy as np
import pandas as pd

from seeq.sdk import *
from seeq.sdk.rest import *
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.workbooks._folder import SYNTHETIC_FOLDERS, synthetic_folder_to_content_filter


def search(query, *, content_filter='owner', all_properties=False, recursive=False, include_archived=False,
           quiet=False, status=None, session: Optional[Session] = None):
    """
    Issues a query to the Seeq Server to retrieve metadata for workbooks.
    This metadata can be used to pull workbook definitions into memory.

    Parameters
    ----------
    query : dict
        A mapping of property / match-criteria pairs. Match criteria uses
        the same syntax as the Data tab in Seeq (contains, or glob, or regex).
        Available options are:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        ID                  ID of the workbook, as seen in the URL.
        Name                Name of the workbook.
        Path                Path to the workbook through the folder hierarchy.
        Description         Description of the workbook.
        Workbook Type       Either 'Analysis' or 'Topic'.
        =================== ===================================================

    content_filter : str, default 'owner'
        The allowed_content_filter must be updated every time there is a change to the ItemWithOwner#Filter
        Filters workbooks according to the following possible values:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        owner               Only content owned by the logged-in user.
        shared              Only content shared specifically with the logged-in
                            user. Note: To obtain the same results as you would
                            when looking at the "Shared" tab in the Seeq home
                            screen, use "sharedorpublic" (see below).
        public              Only content shared with Everyone.
        sharedorpublic      Content shared with Everyone or with the logged-in user
        corporate           Only content in the Corporate folder
        all                 All content, across all users (logged-in user must
                            be admin).
        users               Every user's home folder (logged-in user must be admin)
        =================== ===================================================

    all_properties : bool, default False
        True if all workbook properties should be retrieved. This currently makes
        the search operation much slower as retrieval of properties for an item
        requires a separate call.

    recursive : bool, default False
        True if workbooks further down in the folder path should be returned.

    include_archived : bool, default False
        True if archived (aka "trashed") folders/workbooks should be returned.

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
        A DataFrame with rows for each workbook found and columns for each
        property.

    """
    _common.validate_argument_types([
        (query, 'query', dict),
        (content_filter, 'content_filter', str),
        (all_properties, 'all_properties', bool),
        (recursive, 'recursive', bool),
        (quiet, 'quiet', bool),
        (status, 'status', Status),
        (session, 'session', Session)
    ])

    status = Status.validate(status, quiet)
    session = Session.validate(session)
    _login.validate_login(session, status)

    status.reset_timer()

    try:
        results_df = _search(session, query, content_filter=content_filter, all_properties=all_properties,
                             recursive=recursive, include_archived=include_archived, status=status)

    except KeyboardInterrupt:
        status.update('Query canceled.', Status.CANCELED)
        return

    status.metrics({
        'Results': {
            'Time': status.get_timer(),
            'Count': len(results_df)
        }
    })
    status.update('Query successful.', Status.SUCCESS)

    return results_df


def _search(session: Session, query, *, content_filter, all_properties, recursive, include_archived, parent_id=None,
            parent_path='', search_folder_id=None, status=None):
    items_api = ItemsApi(session.client)
    workbooks_api = WorkbooksApi(session.client)
    results_df = pd.DataFrame()

    content_filter = content_filter.upper()
    allowed_content_filters = ['OWNER', 'SHARED', 'PUBLIC', 'CORPORATE', 'ALL', 'USERS', 'SHAREDORPUBLIC']
    if content_filter not in allowed_content_filters:
        raise SPyValueError('content_filter must be one of: %s' % ', '.join(allowed_content_filters))

    for _key, _ in query.items():
        supported_query_fields = ['ID', 'Path', 'Name', 'Description', 'Workbook Type']
        if _key not in supported_query_fields:
            raise SPyValueError('"%s" unsupported query field, use instead one or more of: %s' %
                                (_key, ', '.join(supported_query_fields)))

    if 'ID' in query:
        try:
            workbook_output = workbooks_api.get_workbook(id=query['ID'])  # type: WorkbookOutputV1
        except ApiException as e:
            if e.status == 404:
                return pd.DataFrame()

            raise

        content_dict = {
            'ID': workbook_output.id,
            'Type': 'Workbook',
            'Workbook Type': workbook_output.type,
            'Path': _common.path_list_to_string([a.name for a in workbook_output.ancestors]),
            'Name': workbook_output.name,
            'Owner Name': workbook_output.owner.name,
            'Owner Username': workbook_output.owner.username,
            'Owner ID': workbook_output.owner.id,
            'Archived': workbook_output.is_archived,
            'Pinned': workbook_output.marked_as_favorite,
            'Created At': pd.to_datetime(workbook_output.created_at),
            'Updated At': pd.to_datetime(workbook_output.updated_at)
        }

        return pd.DataFrame([content_dict])

    path_filter = query['Path'] if 'Path' in query else None

    path_filter_parts = list()
    path_start = None

    if path_filter is not None:
        path_filter_parts = _common.path_string_to_list(path_filter)
        if len(path_filter_parts) > 0:
            path_start = path_filter_parts[0]

    # We want the predefined synthetic folders like workbooks.CORPORATE and workbooks.MY_FOLDER to
    # work as root directories when specified at the beginning of Path
    if path_start in SYNTHETIC_FOLDERS:
        path_start_no_underscore = path_start.replace('__', '').replace('_', ' ')
        warning_message = f'The content_filter {content_filter} was overwritten, and the searched directory was ' \
                          f'set to {path_start_no_underscore} based on the provided path.'

        new_content_filter = synthetic_folder_to_content_filter(path_start)

        if content_filter != new_content_filter and status is not None:
            status.warn(warning_message)
        # Apply the corresponding content_filter and use the rest of the path
        content_filter = new_content_filter
        path_filter_parts.pop(0)
    contents = list()

    def _add_to_folder_contents(archived):
        if parent_id is not None:
            folder_output_list = get_folders(session,
                                             content_filter=content_filter,
                                             folder_id=parent_id,
                                             archived=archived)  # type: WorkbenchItemOutputListV1
        else:
            folder_output_list = get_folders(session,
                                             content_filter=content_filter,
                                             archived=archived)  # type: WorkbenchItemOutputListV1

        contents.extend(folder_output_list.content)

    _add_to_folder_contents(False)
    if include_archived:
        _add_to_folder_contents(True)

    for content in contents:  # type: WorkbenchSearchResultPreviewV1
        path_matches = False
        props_match = True
        if content.type == 'Folder' and len(path_filter_parts) > 0 and \
                _common.does_query_fragment_match(path_filter_parts[0], content.name, contains=False):
            path_matches = True

        for query_key, content_key in [('Name', 'name'), ('Description', 'description')]:
            attr_value = getattr(content, content_key)
            if query_key in query and (attr_value is None or
                                       not _common.does_query_fragment_match(query[query_key],
                                                                             attr_value)):
                props_match = False
                break

        workbook_type = content.type

        if 'Workbook Type' in query and not _common.does_query_fragment_match(query['Workbook Type'], workbook_type):
            props_match = False

        absolute_path = parent_path

        _type = content.type or np.nan
        if _type in ['Analysis', 'Topic']:
            # This is for backward compatibility with .49 and earlier, which used the same type (Workbook) for both
            # Analysis and Topic. Eventually we may want to deprecate "Workbook Type" and fold it into the "Type"
            # property.
            _type = 'Workbook'

        if props_match and len(path_filter_parts) == 0:
            content_dict = {
                'ID': content.id or np.nan,
                'Type': _type,
                'Path': absolute_path,
                'Name': content.name or np.nan,
                'Pinned': content.is_pinned or np.nan,
                'Archived': content.is_archived or np.nan,
                'Created At': pd.to_datetime(content.created_at),
                'Updated At': pd.to_datetime(content.updated_at)
            }

            if search_folder_id:
                content_dict['Search Folder ID'] = search_folder_id

            content_dict['Workbook Type'] = workbook_type

            if all_properties:
                excluded_properties = [
                    # Exclude these because they're in ns-since-epoch when we retrieve them this way
                    'Created At', 'Updated At',

                    # Exclude this because it's a bunch of JSON that will clutter up the DataFrame
                    'Data', 'workbookState'
                ]

                _item = items_api.get_item_and_all_properties(id=content.id)  # type: ItemOutputV1
                for prop in _item.properties:  # type: PropertyOutputV1

                    if prop.name in excluded_properties:
                        continue

                    content_dict[prop.name] = _common.none_to_nan(prop.value)

            results_df = results_df.append(content_dict, ignore_index=True, sort=True)

        if content.type == 'Folder' and ((recursive and len(path_filter_parts) == 0) or path_matches):
            child_path_filter = None
            if path_filter_parts and len(path_filter_parts) > 1:
                child_path_filter = _common.path_list_to_string(path_filter_parts[1:])

            if len(parent_path) == 0:
                new_parent_path = content.name
            else:
                new_parent_path = parent_path + ' >> ' + content.name

            child_query = dict(query)
            if not child_path_filter and 'Path' in child_query:
                # We've finished drilling down using the provided 'Path' so now we can use the current folder ID as the
                # "root" from which all paths can be made relative (if desired)
                search_folder_id = content.id
                del child_query['Path']
            else:
                child_query['Path'] = child_path_filter

            child_results_df = _search(session, child_query, content_filter=content_filter,
                                       all_properties=all_properties, recursive=recursive,
                                       include_archived=include_archived, parent_id=content.id,
                                       parent_path=new_parent_path, search_folder_id=search_folder_id)

            results_df = results_df.append(child_results_df, ignore_index=True, sort=True)

    return results_df


def get_folders(session: Session, content_filter='ALL', folder_id=None, archived=False, sort_order='createdAt ASC',
                only_pinned=False) -> WorkbenchItemOutputListV1:
    folders_api = FoldersApi(session.client)

    kwargs = {
        'is_archived': archived,
        'sort_order': sort_order,
        'limit': 100000,
        'only_pinned': only_pinned
    }

    if folder_id:
        kwargs['folder_id'] = folder_id
    elif content_filter in ('OWNER', 'CORPORATE', 'USERS'):
        kwargs['folder_id'] = content_filter
    else:
        kwargs['filter'] = content_filter

    folders = folders_api.get_folders(**kwargs)

    return folders
