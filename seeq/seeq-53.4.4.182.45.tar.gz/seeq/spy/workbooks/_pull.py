from typing import List, Optional, Union

import pandas as pd

from seeq import spy
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.workbooks._workbook import Workbook


def pull(workbooks_df: Union[pd.DataFrame, str], *, include_referenced_workbooks: bool = True,
         include_inventory: bool = True, include_images: bool = True, include_rendered_content: bool = False,
         specific_worksheet_ids: Optional[List[str]] = None, errors: str = 'raise', quiet: bool = False,
         status: Optional[Status] = None, session: Optional[Session] = None) -> Optional[List[Workbook]]:
    """
    Pulls the definitions for each workbook specified by workbooks_df into
    memory as a list of Workbook items.

    Parameters
    ----------
    workbooks_df : {str, pd.DataFrame}
        A DataFrame containing 'ID', 'Type' and 'Workbook Type' columns that
        can be used to identify the workbooks to pull. This is usually created
        via a call to spy.workbooks.search(). Alternatively, you can supply URL
        of a Seeq Workbench worksheet as a str.

    include_referenced_workbooks : bool, default True
        If True, Analyses that are depended upon by Topics will be
        automatically included in the resulting list even if they were not part
        of the workbooks_df DataFrame.

    include_inventory : bool, default True
        If True, all items that are referenced in worksheets, journals, topics
        etc are included in the Workbook object's "inventory", along with
        anything that is scoped to the workbook.

    include_images : bool, default True
        If True, downloads all static images (not including embedded content --
        see include_rendered_content for that).

    include_rendered_content : bool, default False
        If True, any Organizer Topics pulled will include rendered content
        images, which will cause spy.workbooks.save() to include a folder for
        each Topic Document with its HTML and images such that it can be loaded
        and viewed in a browser.

    specific_worksheet_ids : List[str], default None
        If supplied, only the worksheets with IDs specified in the supplied
        list will be pulled. This should be used when it would otherwise take
        too long to pull all worksheets and you're only interested in a small
        subset. Be careful not to push the resulting workbook(s) back because
        the other worksheets will get archived.

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
        (workbooks_df, 'workbooks_df', (pd.DataFrame, str)),
        (include_referenced_workbooks, 'include_referenced_workbooks', bool),
        (include_inventory, 'include_inventory', bool),
        (include_images, 'include_images', bool),
        (include_rendered_content, 'include_rendered_content', bool),
        (errors, 'errors', str),
        (quiet, 'quiet', bool),
        (status, 'status', Status),
        (session, 'session', Session)
    ])

    status = Status.validate(status, quiet)
    session = Session.validate(session)
    _login.validate_login(session, status)

    _common.validate_errors_arg(errors)
    _common.validate_unique_dataframe_index(workbooks_df, 'workbooks_df')

    if isinstance(workbooks_df, str):
        # If workbooks_df is a URL, get the actual items from the worksheet and overwrite workbooks_df as a DataFrame
        url = workbooks_df
        workbooks_df = spy.workbooks.search({'ID': spy.utils.get_workbook_id_from_url(url)},
                                            quiet=True, status=status.create_inner('Workbook URL Search'),
                                            session=session)
        if len(workbooks_df) == 0:
            raise SPyValueError(f'"{url}" is not a workbook URL')

    if len(workbooks_df) == 0:
        status.update('workbooks_df is empty', Status.SUCCESS)
        return list()

    for required_column in ['ID', 'Type', 'Workbook Type']:
        if required_column not in workbooks_df.columns:
            raise SPyValueError('"%s" column must be included in workbooks_df' % required_column)

    status_columns = list()

    for col in ['ID', 'Name', 'Workbook Type']:
        if col in workbooks_df:
            status_columns.append(col)

    workbooks_df = workbooks_df[workbooks_df['Type'] != 'Folder']

    status.df = workbooks_df[status_columns].copy().reset_index(drop=True)
    status.df['Count'] = 0
    status.df['Time'] = 0
    status.df['Result'] = 'Queued'
    status_columns.extend(['Count', 'Time', 'Result'])

    status.update('Pulling workbooks', Status.RUNNING)

    workbooks_to_pull = {_common.get(row, 'ID'): {
        'Index': index,
        'Workbook Type': _common.get(row, 'Workbook Type'),
        'Search Folder ID': _common.get(row, 'Search Folder ID'),
        'Worksteps': set()
    } for index, row in workbooks_df.iterrows()}

    # Process Topics first so that we can discover Analyses and Worksteps (of embedded content) to add to our list (
    # assuming include_referenced_workbooks is True). Note that it is possible for Analyses to reference Topics (via
    # a link in a Journal) and they will not be properly included in the output. We have accepted this hole because
    # otherwise if we add a Topic to our list and that Topic refers to a workstep in an already-processed Analysis,
    # we would have to go back and re-pull the Analysis. (Maybe someday we'll do that, but not now. :-) )
    for phase in ['Topic', 'Analysis']:
        while True:
            at_least_one_item_pulled = False
            for item_id, pull_info in workbooks_to_pull.copy().items():
                try:
                    if not isinstance(pull_info, dict):
                        # Already pulled
                        continue

                    if pull_info['Workbook Type'] != phase:
                        continue

                    status.reset_timer()
                    status.current_df_index = pull_info['Index']
                    status.put('Result', 'Pulling')

                    workbook = Workbook.pull(item_id,
                                             extra_workstep_tuples=pull_info['Worksteps'],
                                             specific_worksheet_ids=specific_worksheet_ids,
                                             include_inventory=include_inventory,
                                             include_images=include_images,
                                             status=status,
                                             session=session)  # type: Workbook

                    if include_rendered_content:
                        status.put('Result', 'Pulling rendered content')
                        workbook.pull_rendered_content(errors=errors, quiet=quiet,
                                                       status=status.create_inner(
                                                           f'Pull Embedded Content {workbook}'),
                                                       session=session)

                    # The "Search Folder ID" is a means by which we can establish "relative paths" like a file
                    # system. The idea is that whatever folder you specified for spy.workbooks.search() is probably
                    # the folder to serve as the "start" and all subfolders become relative to whatever folder is
                    # specified as the "start" during the spy.workbook.push() call. ("start" in this case is very
                    # similar to os.path.relpath()'s "start" argument.) If we didn't have this relative mechanism, it
                    # would be difficult to take a folder full of stuff and duplicate it or put it in a new/different
                    # location.
                    if pull_info['Search Folder ID']:
                        workbook['Search Folder ID'] = pull_info['Search Folder ID']
                    elif len(workbook['Ancestors']) > 0:
                        # If there was no Search Folder ID in the pull_info BUT there are Ancestors, that means this
                        # workbook is being pulled without having done spy.workbook.search() first. If so, then make
                        # the closest ancestor folder its "start", that way when spy.workbooks.push() comes around,
                        # it won't be trying to push any containing folders.
                        workbook['Search Folder ID'] = workbook['Ancestors'][-1]

                    if include_referenced_workbooks:
                        def _add_if_necessary(_workbook_id, _workstep_tuples):
                            if _workbook_id not in workbooks_to_pull:
                                to_add_df = spy.workbooks.search({'ID': _workbook_id},
                                                                 status=status.create_inner(
                                                                     f'Find Workbook {_workbook_id}',
                                                                     quiet=True),
                                                                 session=session)
                                if len(to_add_df) == 0:
                                    # Workbook with this ID not found, probably as a result of a tool making an
                                    # invalid link in a Journal or Topic Document.
                                    return

                                workbook_type_to_add = _common.get(to_add_df.iloc[0], 'Workbook Type')
                                if phase == 'Analysis' and workbook_type_to_add == 'Topic':
                                    # We can't process more Topics once we're in the Analysis phase. (See comment
                                    # above the "for phase" loop.)
                                    return

                                workbooks_to_pull[_workbook_id] = {
                                    'Index': len(status.df),
                                    'Workbook Type': workbook_type_to_add,
                                    'Search Folder ID': pull_info['Search Folder ID'],
                                    'Worksteps': set()
                                }

                                to_add_df['Count'] = 0
                                to_add_df['Time'] = 0
                                to_add_df['Result'] = 'Queued'
                                status.df.loc[len(status.df)] = to_add_df.iloc[0][status_columns]

                            if not isinstance(workbooks_to_pull[_workbook_id], dict):
                                # We've already pulled it, that ship has sailed. This can happen when there are a
                                # web of links between Topics / Journals. We only do a "best effort" to make the
                                # links work.
                                return

                            workbooks_to_pull[_workbook_id]['Worksteps'].update(_workstep_tuples)

                        for workbook_id, workstep_tuples in workbook.referenced_workbooks.items():
                            _add_if_necessary(workbook_id, workstep_tuples)

                        for workbook_id, workstep_tuples in workbook.find_workbook_links(session).items():
                            _add_if_necessary(workbook_id, workstep_tuples)

                    workbooks_to_pull[item_id] = workbook
                    at_least_one_item_pulled = True

                    status.put('Time', status.get_timer())
                    status.put('Result', 'Success')

                    if len(workbook.item_pull_errors) > 0:
                        raise SPyRuntimeError(workbook.items_pull_errors_str)

                except BaseException as e:
                    _common.raise_or_catalog(errors, status, e=e)

            if not at_least_one_item_pulled:
                break

    status.update('Pull successful', Status.SUCCESS)

    return list(workbooks_to_pull.values())
