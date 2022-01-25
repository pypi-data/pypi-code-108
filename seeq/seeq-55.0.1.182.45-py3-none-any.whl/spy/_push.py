import datetime
import re
import types
from typing import Optional

import numpy as np
import pandas as pd

from seeq import spy
from seeq.sdk import *
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy import _metadata
from seeq.spy._common import EMPTY_GUID
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status


def push(data=None, *, metadata=None, replace=None, workbook=_common.DEFAULT_WORKBOOK_PATH,
         worksheet=_common.DEFAULT_WORKSHEET_NAME, datasource=None, archive=False, type_mismatches='raise',
         errors='raise', quiet=False, status=None, session: Optional[Session] = None):
    """
    Imports metadata and/or data into Seeq Server, possibly scoped to a
    workbook and/or datasource.

    The 'data' and 'metadata' arguments work together. Signal and condition
    data cannot be mixed together in a single call to spy.push().

    Successive calls to 'push()' with the same 'metadata' but different 'data'
    will update the items (rather than overwrite them); however, pushing a new
    sample with the same timestamp as a previous one will overwrite the old
    one.

    Metadata can be pushed without accompanying data. This is common after
    having invoked the spy.assets.build() function. In such a case, the
    'metadata' DataFrame can contain signals, conditions, scalars or assets.

    Parameters
    ----------
    data : pandas.DataFrame, optional
        A DataFrame that contains the signal or condition data to be pushed.
        If 'metadata' is also supplied, it will have specific formatting
        requirements depending on the type of data being pushed.

        For signals, 'data' must have a pandas.Timestamp-based index with a
        column for each signal. To push to an existing signal, set the column
        name to the Seeq ID of the item to be pushed. An exception will be
        raised if the item does not exist.

        For conditions, 'data' must have an integer index and two
        pandas.Timestamp columns named 'Capsule Start' and 'Capsule End'.

    metadata : pandas.DataFrame, optional
        A DataFrame that contains the metadata for signals, conditions,
        scalars, metrics, or assets. If 'metadata' is supplied, in conjunction
        with a 'data' DataFrame, it has specific requirements depending on the
        kind of data supplied.

        For signals, the 'metadata' index (i.e., each row's index value) must
        match the column names of the 'data' DataFrame. For example, if you
        would like to push data where the name of each column is the Name of
        the item, then you might do set_index('Name', inplace=True, drop=False)
        on your metadata DataFrame to make the index match the data DataFrame's
        column names.

        For conditions and metrics, the 'metadata' DataFrame must have only
        one row with metadata.

        Metadata for each object type includes:

        Type Key:   Si = Signal, Sc = Scalar, C = Condition,
                    A = Asset, M = Metric

        ===================== ==================================== ============
        Metadata Term         Definition                           Types
        ===================== ==================================== ============
        Name                  Name of the signal                   Si,Sc,C,A,M
        Description           Description of the signal            Si,Sc,C,A
        Maximum Interpolation Maximum interpolation between        Si
                              samples
        Value Unit Of Measure Unit of measure for the signal       Si
        Formula               Formula for a calculated item        Si,Sc,C
        Formula Parameters    Parameters for a formula             Si,Sc,C
        Interpolation Method  Interpolation method between points  Si
                              Options are Linear, Step, PILinear
        Maximum Duration      Maximum expected duration for a      C
                              capsule
        Number Format         Formatting string ECMA-376           Si,Sc,M
        Path                  Asset tree path where the item's     Si,Sc,C,A
                              parent asset resides
        Measured Item         The ID of the signal or condition    M
        Statistic             Aggregate formula function to        M
                              compute on the measured item
        Duration              Duration to calculate a moving       M
                              aggregation for a continuous process
        Period                Period to sample for a               M
                              continuous process
        Thresholds            List of priority thresholds mapped
                              to a scalar formula/value or an ID   M
                              of a signal, condition or scalar
        Bounding Condition    The ID of a condition to aggregate   M
                              for a batch process
        Bounding Condition    Duration for aggregation for a       M
        Maximum Duration      bounding condition without a maximum
                              duration
        Asset                 Parent asset name. Parent asset      Si,Sc,C,A,M
                              must be in the tree at the
                              specified path, or listed in
                              'metadata' for creation.
        ===================== ==================================== ============

    replace : dict, default None
        A dict with the keys 'Start' and 'End'.
        If provided, the capsules with the start date in the provided time period will be replaced.
        The condition whose capsules are going to be replaced must be specified in metadata.
        Start of the time period is inclusive and the end of the time period is exclusive.

    workbook : {str, None}, default 'Data Lab >> Data Lab Analysis'
        The path to a workbook (in the form of 'Folder >> Path >> Workbook
        Name') or an ID that all pushed items will be 'scoped to'. Items scoped
        to a certain workbook will not be visible/searchable using the data
        panel in other workbooks. If None, items can also be 'globally scoped',
        meaning that they will be visible/searchable in all workbooks. Global
        scoping should be used judiciously to prevent search results becoming
        cluttered in all workbooks. The ID for a workbook is visible in the URL
        of Seeq Workbench, directly after the "workbook/" part. You can also
        push to the Corporate folder by using the following pattern:
        f'{spy.workbooks.CORPORATE} >> MySubfolder >> MyWorkbook'

    worksheet : {str, None}, default 'From Data Lab'
        The name of a worksheet within the workbook to create/update that will
        render the data that has been pushed so that you can see it in Seeq
        easily. If None, no worksheet will be added or changed.

    datasource : str, optional
        The name of the datasource within which to contain all the
        pushed items. By default, all pushed items will be contained in a "Seeq
        Data Lab" datasource. Do not create new datasources unless you really
        want to and you have permission from your administrator.

    archive : bool, default False
        If True, and all metadata describes items from a common asset tree, then
        items in the tree not updated by this push call are archived.

    type_mismatches : {'raise', 'drop', 'invalid'}, default 'raise'
        If 'raise' (default), any mismatches between the type of the data and
        its metadata will cause an exception. For example, if string data is
        found in a numeric time series, an error will be raised. If 'drop' is
        specified, such data will be ignored while pushing. If 'invalid' is
        specified, such data will be replaced with an INVALID sample, which
        will interrupt interpolation in calculations and displays.

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

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the metadata for the items pushed, along with any
        errors and statistics about the operation.

        Additionally, the following properties are stored on the "spy"
        attribute of the output DataFrame:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        func                A str value of 'spy.push'
        kwargs              A dict with the values of the input parameters
                            passed to spy.push to get the output DataFrame
        workbook_id         If pushed to a specific workbook, the ID of that
                            workbook.
        workbook_url        If pushed to a specific workbook, the URL of that
                            workbook and the curated worksheet that this
                            command created.
        status              A spy.Status object with the status of the
                            spy.push call
        =================== ===================================================
    """
    input_args = _common.validate_argument_types([
        (data, 'data', pd.DataFrame),
        (metadata, 'metadata', pd.DataFrame),
        (replace, 'replace', dict),
        (workbook, 'workbook', str),
        (worksheet, 'worksheet', str),
        (datasource, 'datasource', str),
        (archive, 'archive', bool),
        (type_mismatches, 'type_mismatches', str),
        (errors, 'errors', str),
        (quiet, 'quiet', bool),
        (status, 'status', Status),
        (session, 'session', Session)
    ])

    status = Status.validate(status, quiet)
    session = Session.validate(session)
    _login.validate_login(session, status)

    _common.validate_errors_arg(errors)

    if type_mismatches not in ['drop', 'raise', 'invalid']:
        raise SPyValueError("'type_mismatches' must be either 'drop', 'raise' or 'invalid'")

    if replace is not None:
        if replace.keys() != {'Start', 'End'}:  # strict comparison, allowing only these two keys
            raise SPyValueError(f"Parameter 'replace'' must have 'Start' and 'End' keys. Given keys: "
                                f"{replace.keys()}")

    tree_root = None
    if archive:
        if metadata is None or metadata.empty:
            raise SPyValueError("Asset tree metadata must be provided when parameter 'archive' is 'tree'.")
        tree_root = get_common_root(metadata)
        if tree_root is None:
            raise SPyValueError("Items in metadata must all belong to the same asset tree when parameter "
                                "'archive' is True.")

    item_type = 'Signal'
    if data is not None:
        if 'Capsule Start' in data.columns or 'Capsule End' in data.columns:
            item_type = 'Condition'
    elif metadata is not None:
        if 'Type' in metadata.columns and not metadata.empty and metadata.iloc[0]['Type'] == 'Condition':
            item_type = 'Condition'

    datasource_output = _metadata.create_datasource(session, datasource)

    primary_workbook = None
    primary_worksheet = None
    workbook_id = None
    folder_id = None
    if workbook is not None:
        if worksheet is not None and not isinstance(worksheet, str):
            raise SPyValueError('When workbook is supplied, worksheet must also be supplied as a string')

        if _common.is_guid(workbook):
            primary_workbooks = spy.workbooks.pull(pd.DataFrame([{
                'ID': _common.sanitize_guid(workbook),
                'Type': 'Workbook',
                'Workbook Type': 'Analysis'
            }]), include_inventory=False, status=status.create_inner('Pull Workbook', quiet=True), session=session)

            if len(primary_workbooks) == 0:
                raise SPyRuntimeError(f'Workbook with ID "{_common.sanitize_guid(workbook)}" not found')

            primary_workbook = primary_workbooks[0]
        else:
            search_query, workbook_name = create_analysis_search_query(workbook)
            search_df = spy.workbooks.search(search_query, quiet=True, session=session)
            if len(search_df) == 0:
                primary_workbook = spy.workbooks.Analysis({'Name': workbook_name})
                primary_workbook.worksheet(worksheet if worksheet else _common.DEFAULT_WORKSHEET_NAME)
                spy.workbooks.push(primary_workbook, path=_common.get(search_query, 'Path'), include_inventory=False,
                                   datasource=datasource, status=status.create_inner('Create Workbook', quiet=True),
                                   session=session)
            else:
                primary_workbook = spy.workbooks.pull(search_df, include_inventory=False,
                                                      status=status.create_inner('Pull Workbook', quiet=True),
                                                      session=session)[0]

        workbook_id = primary_workbook.id
        if len(primary_workbook['Ancestors']) > 0:
            folder_id = primary_workbook['Ancestors'][-1]

    push_result_df = pd.DataFrame()  # type: pd.DataFrame
    sync_token = datetime.datetime.utcnow().isoformat()
    if metadata is not None and not metadata.empty:
        push_result_df = _metadata.push(session, metadata, workbook_id, datasource_output, sync_token, errors,
                                        status.create_inner('Push Metadata'))  # type: pd.DataFrame

    if archive:
        status.update(f'Archiving obsolete items in Asset Tree <strong>{tree_root}</strong> scoped to '
                      f'workbook ID <strong>{workbook_id}</strong>.', Status.RUNNING)

        datasource_clean_up_input = DatasourceCleanUpInputV1()
        datasource_clean_up_input.sync_token = sync_token
        datasource_clean_up_input.item_data_id_regex_filter = _tree_root_to_data_id_regex(workbook_id, tree_root)
        datasources_api = DatasourcesApi(session.client)
        datasources_api.clean_up(id=datasource_output.id, body=datasource_clean_up_input)

    sample_stats = types.SimpleNamespace(earliest_sample_in_ms=None, latest_sample_in_ms=None)

    def _on_success(_row_index, _job_result):
        _earliest_sample_in_ms, _latest_sample_in_ms, item_id = _job_result
        if None not in [sample_stats.earliest_sample_in_ms, _earliest_sample_in_ms]:
            sample_stats.earliest_sample_in_ms = min(_earliest_sample_in_ms, sample_stats.earliest_sample_in_ms)
        elif sample_stats.earliest_sample_in_ms is None and _earliest_sample_in_ms is not None:
            sample_stats.earliest_sample_in_ms = _earliest_sample_in_ms

        if None not in [sample_stats.latest_sample_in_ms, _latest_sample_in_ms]:
            sample_stats.latest_sample_in_ms = max(_latest_sample_in_ms, sample_stats.latest_sample_in_ms)
        elif sample_stats.latest_sample_in_ms is None and _latest_sample_in_ms is not None:
            sample_stats.latest_sample_in_ms = _latest_sample_in_ms

        if item_id is None:
            # This can happen if the column has only nan values. In that case, we don't know whether
            # it's a string or numeric signal and we couldn't create the signal item.
            # Check to see if it was created by push_metadata.
            if 'ID' in signal_metadata:
                item_id = signal_metadata['ID']

            # CRAB-19586: Cannot convert string to float error
            # Since the ID column has only nan values, ensure ID column is dtype object
            push_result_df['ID'] = push_result_df['ID'].astype(object)

        push_result_df.at[_row_index, 'ID'] = item_id
        push_result_df.at[_row_index, 'Type'] = \
            'StoredSignal' if item_type == 'Signal' else 'StoredCondition'

    if data is not None or replace is not None:
        def _put_item_defaults(d):
            if not _common.present(d, 'Datasource Class'):
                d['Datasource Class'] = datasource_output.datasource_class

            if not _common.present(d, 'Datasource ID'):
                d['Datasource ID'] = datasource_output.datasource_id

            if not _common.present(d, 'Type'):
                d['Type'] = item_type

            if not _common.present(d, 'Data ID'):
                d['Data ID'] = _metadata.get_scoped_data_id(d, workbook_id)

            if not _common.present(d, 'Scoped To') and workbook_id is not None:
                d['Scoped To'] = workbook_id

        status_columns = list()
        if 'ID' in push_result_df:
            status_columns.append('ID')
        if 'Path' in push_result_df:
            status_columns.append('Path')
        if 'Asset' in push_result_df:
            status_columns.append('Asset')
        if 'Name' in push_result_df:
            status_columns.append('Name')

        status.df = push_result_df[status_columns].copy()
        status.df['Count'] = 0
        status.df['Pages'] = 0
        status.df['Time'] = 0
        status.df['Result'] = 'Pushing'
        status_columns.extend(['Count', 'Pages', 'Time', 'Result'])

        push_result_df['Push Count'] = np.int64(0)
        push_result_df['Push Time'] = 0
        push_result_df['Push Result'] = ''

        status.update(
            f'Pushing data to datasource <strong>{datasource_output.name} ['
            f'{datasource_output.datasource_id}]</strong> scoped to workbook ID '
            f'<strong>{workbook_id}</strong>',
            Status.RUNNING)

        if data is not None and item_type == 'Signal':
            for column in data:
                try:
                    status_index = column

                    # For performance reasons, this variable will be supplied to _push_signal() if we had to
                    # retrieve the signal as part of this function
                    signal_output: Optional[SignalOutputV1] = None

                    if status_index in push_result_df.index:
                        # push_result_df will be filled in by _metadata.push() if a metadata DataFrame was
                        # supplied, so grab the metadata out of there for the signal
                        signal_metadata = push_result_df.loc[status_index].to_dict()

                    elif _common.is_guid(status_index):
                        # If an ID is supplied as the column name, then we are pushing to an existing signal and
                        # we need to query that signal for a few pieces of metadata.
                        signals_api = SignalsApi(session.client)
                        signal_output = signals_api.get_signal(id=status_index)
                        signal_metadata = {
                            # This is the metadata needed to process the samples appropriately in _push_signal()
                            'Name': signal_output.name,
                            'Type': signal_output.type,
                            'Value Unit Of Measure': signal_output.value_unit_of_measure
                        }

                    else:
                        # Metadata has not been supplied and the column name is not an ID, so just create a
                        # "blank" row in the status DataFrame.
                        ad_hoc_status_df = pd.DataFrame({'Count': 0, 'Pages': 0, 'Time': 0, 'Result': 'Pushing'},
                                                        index=[status_index])
                        status.df = status.df.append(ad_hoc_status_df, sort=True)
                        status.update()
                        signal_metadata = dict()

                    if not _common.present(signal_metadata, 'Name'):
                        if '>>' in column:
                            raise SPyRuntimeError(
                                'Paths in column name not currently supported. Supply a metadata argument if you '
                                'would like to put signal(s) directly in an asset tree.')

                        signal_metadata['Name'] = column

                    if not signal_output:
                        # Plant the "default" metadata so that the item will be placed in the specified
                        # datasource and its Data ID will be managed by SPy
                        _put_item_defaults(signal_metadata)

                    push_result_df.at[status_index, 'Name'] = signal_metadata['Name']

                    status.add_job(status_index,
                                   (_push_signal, session, column, signal_metadata, replace, data, signal_output,
                                    type_mismatches, status_index, status),
                                   _on_success)

                except BaseException as e:
                    _common.raise_or_catalog(errors, status=status, df=push_result_df, index=column,
                                             column='Push Result', e=e)

        elif data is not None and item_type == 'Condition':
            try:
                if metadata is None or len(metadata) != 1:
                    raise SPyRuntimeError('Condition requires "metadata" input of DataFrame with single row')

                condition_metadata = metadata.iloc[0].to_dict()

                if 'Name' not in condition_metadata or 'Maximum Duration' not in condition_metadata:
                    raise SPyRuntimeError('Condition metadata requires "Name" and "Maximum Duration" columns')

                if 'Capsule Start' not in data or 'Capsule End' not in data:
                    raise SPyRuntimeError('Condition data requires "Capsule Start" and "Capsule End" columns')

                _put_item_defaults(condition_metadata)

                push_result_df.at[0, 'Name'] = condition_metadata['Name']

                status.add_job(0,
                               (_push_condition, session, condition_metadata, replace, data, 0, status),
                               _on_success)

            except BaseException as e:
                _common.raise_or_catalog(errors, status=status, df=push_result_df, index=0,
                                         column='Push Result', e=e)

        else:
            for status_index, row in push_result_df.iterrows():
                try:
                    if 'StoredSignal' in _common.get(row, 'Type'):
                        signal_metadata = row.to_dict()
                        _put_item_defaults(signal_metadata)
                        status.add_job(status_index,
                                       (_push_signal, session, None, signal_metadata, replace, None, None,
                                        type_mismatches, status_index, status),
                                       _on_success)

                    elif 'StoredCondition' in _common.get(row, 'Type'):
                        condition_metadata = row.to_dict()
                        _put_item_defaults(condition_metadata)
                        status.add_job(status_index,
                                       (_push_condition, session, condition_metadata, replace, data, status_index,
                                        status))
                except BaseException as e:
                    _common.raise_or_catalog(errors, status=status, df=push_result_df, index=status_index,
                                             column='Push Result', e=e)

        status.execute_jobs(session, errors)

        for status_index, status_row in status.df.iterrows():
            push_result_df.at[
                status_index, 'Push Result'] = status.df.at[status_index, 'Result']
            push_result_df.at[status_index, 'Push Count'] = status.df.at[status_index, 'Count']
            push_result_df.at[status_index, 'Push Time'] = status.df.at[status_index, 'Time']

    workbooks_to_push = list()
    if metadata is not None and 'Type' in metadata.columns:
        workbook_rows = metadata[metadata['Type'] == 'Workbook']
        for _, workbook_row in workbook_rows.iterrows():
            workbook_object = workbook_row['Object']  # type: spy.workbooks.Workbook
            if workbook_object.name is None:
                workbook_object.name = primary_workbook.name if primary_workbook else _common.DEFAULT_WORKBOOK_NAME
            if isinstance(workbook_object, spy.workbooks.Analysis) and \
               workbook_object.name == primary_workbook.name if primary_workbook else _common.DEFAULT_WORKBOOK_NAME:
                primary_workbook = workbook_object

            for worksheet_object in workbook_object.worksheets:
                if worksheet_object.name is None:
                    worksheet_object.name = worksheet if worksheet else _common.DEFAULT_WORKSHEET_NAME

            workbooks_to_push.append(workbook_object)

    if primary_workbook:
        if len([w for w in workbooks_to_push if isinstance(w, spy.workbooks.Analysis)]) == 0:
            workbooks_to_push.append(primary_workbook)
            if worksheet is not None:
                primary_worksheet = primary_workbook.worksheet(worksheet)
                _auto_populate_worksheet(sample_stats.earliest_sample_in_ms, sample_stats.latest_sample_in_ms,
                                         replace, push_result_df, primary_worksheet)
            else:
                # User does not want to render any changes in trendview so do not update display_items,
                # just get worksheet
                primary_worksheet = primary_workbook.worksheets[0]
        else:
            # User is creating worksheets through metadata
            # Get the primary worksheet so we can build up a correct link url
            primary_worksheet = _get_primary_worksheet(session, primary_workbook, folder_id)

    if metadata is not None and 'Asset Object' in metadata.columns:
        for _, _row in metadata.iterrows():
            asset_object = _row['Asset Object']
            if not pd.isna(asset_object):
                asset_object.context.push_df = push_result_df

    # Here we cover the case where an admin is pushing data to a single workbook that they don't own. In R51,
    # there's a proper user folder in the path that can be used as the folder_id. In R50 there is no such user folder,
    # so the folder_id will end up being __All__ or __Shared__, which is not viable to use as a parent folder. But in
    # the case where we're pushing to only the primary workbook, then we don't need to supply the folder_id because the
    # workbook is not being moved and we're not adding other sibling workbooks (and therefore we don't need to know
    # the actual folder that the workbook is in).
    if folder_id in spy.workbooks.SYNTHETIC_FOLDERS and \
            len(workbooks_to_push) == 1 and \
            workbooks_to_push[0] == primary_workbook:
        folder_id = None

    workbook_push_df = None
    if worksheet is not None:
        workbook_push_df = _push_workbooks(session, push_result_df, folder_id, workbooks_to_push, datasource, status)

    primary_link_url = None
    primary_id = None
    if primary_workbook:
        if workbook_push_df is not None and worksheet is not None:
            primary = workbook_push_df[workbook_push_df['ID'] == primary_workbook.id].iloc[0]
            primary_id = primary['Pushed Workbook ID']
            primary_link_url = primary['URL']
        else:
            primary_id = workbook_id
            primary_link_url = '%s/%sworkbook/%s/worksheet/%s' % (
                session.public_url,
                (folder_id + '/') if folder_id is not None else '',
                primary_id,
                primary_worksheet.id
            )
        scope_string = 'and scoped to workbook ID <strong>%s</strong><br>Click the following link to see what ' \
                       'you pushed in Seeq:<br><a href="%s" target="_new">%s</a>' % (primary_id,
                                                                                     primary_link_url,
                                                                                     primary_link_url)
    else:
        scope_string = 'and globally scoped.'

    status.update(
        'Pushed successfully to datasource <strong>%s [Datasource ID: %s]</strong> %s' % (
            datasource_output.name, datasource_output.datasource_id, scope_string),
        Status.SUCCESS)

    push_df_properties = types.SimpleNamespace(
        func='spy.push',
        kwargs=input_args,
        workbook_id=primary_id,
        workbook_url=primary_link_url,
        status=status)

    _common.put_properties_on_df(push_result_df, push_df_properties)

    return push_result_df


def _get_primary_worksheet(session: Session, workbook, folder_id):
    workbooks_api = WorkbooksApi(session.client)
    workbook_id = spy.workbooks.Workbook.find_by_name(session, workbook.name, workbook.definition['Workbook Type'],
                                                      folder_id).id

    if workbook_id is not None:
        worksheet_output_list = workbooks_api.get_worksheets(workbook_id=workbook_id, is_archived=False, offset=0,
                                                             limit=1)
        if (worksheet_output_list and len(worksheet_output_list.worksheets) > 0 and
                worksheet_output_list.worksheets[0] is not None):
            return worksheet_output_list.worksheets[0]
        else:
            raise SPyRuntimeError(f'No worksheet found for workbook: {workbook.name}')
    else:
        raise SPyRuntimeError(f'Could not find a workbook in folder with ID: {folder_id}')


def _auto_populate_worksheet(earliest_sample_in_ms, latest_sample_in_ms, replace, push_result_df, worksheet_object):
    display_items = pd.DataFrame()

    if 'Type' in push_result_df:
        display_items = push_result_df[push_result_df['Type'].isin(['StoredSignal', 'CalculatedSignal',
                                                                    'StoredCondition', 'CalculatedCondition',
                                                                    'CalculatedScalar', 'Chart',
                                                                    'ThresholdMetric'])]

    worksheet_object.display_items = display_items.head(10)
    if earliest_sample_in_ms is not None and latest_sample_in_ms is not None:
        _range = {
            'Start': pd.Timestamp(int(earliest_sample_in_ms) * 1000000, tz='UTC'),
            'End': pd.Timestamp(int(latest_sample_in_ms) * 1000000, tz='UTC')
        }
        worksheet_object.display_range = _range
        worksheet_object.investigate_range = _range
    elif replace is not None:
        _range = replace
        worksheet_object.display_range = _range
        worksheet_object.investigate_range = _range


def create_analysis_search_query(workbook):
    workbook_spec_parts = _common.path_string_to_list(workbook)
    search_query = dict()
    if len(workbook_spec_parts) > 1:
        search_query['Path'] = _common.path_list_to_string(workbook_spec_parts[0:-1])
        workbook_name = workbook_spec_parts[-1]
    else:
        workbook_name = workbook_spec_parts[0]
    search_query['Name'] = f'/^{re.escape(workbook_name)}$/'
    search_query['Workbook Type'] = 'Analysis'
    return search_query, workbook_name


def _push_signal(session: Session, column, signal_metadata, replace, data, signal_output, type_mismatches, status_index,
                 status: Status):
    signals_api = SignalsApi(session.client)
    signal_input = SignalInputV1()
    _metadata.dict_to_signal_input(signal_metadata, signal_input)
    if replace is not None:
        add_samples_input = SamplesOverwriteInputV1()
    else:
        add_samples_input = SamplesInputV1()
    add_samples_input.samples = list()
    count = 0
    page_count = 0
    is_string = None
    # noinspection PyTypeChecker
    timer = _common.timer_start()
    earliest_sample_in_ms = None
    latest_sample_in_ms = None

    def _put_signal(_signal_metadata, _signal_input):
        return signals_api.put_signal_by_data_id(datasource_class=_signal_metadata['Datasource Class'],
                                                 datasource_id=_signal_metadata['Datasource ID'],
                                                 data_id=_signal_metadata['Data ID'],
                                                 body=_signal_input)  # type: SignalOutputV1

    if replace is not None:
        pd_start, pd_end = _login.validate_start_and_end(session, replace['Start'], replace['End'])
        interval_input = IntervalV1()
        interval_input.start = pd_start
        interval_input.end = pd_end
        add_samples_input.interval = interval_input

    if data is not None:
        # Performance notes: It was found that pulling out the column as a pd.Series and then using series.iteritems()
        #                    instead of doing data.iterrows() was 5x-6x faster
        series = data[column]  # type: pd.Series
        for index, sample_value in series.iteritems():
            if pd.isna(sample_value) and sample_value is not None:
                continue

            if not isinstance(index, pd.Timestamp):
                raise SPyRuntimeError('data index must only be pd.Timestamp objects, but %s found instead' %
                                      type(index))

            if is_string is None:
                if _common.present(signal_metadata, 'Value Unit Of Measure'):
                    is_string = (signal_metadata['Value Unit Of Measure'].lower() == 'string')
                else:
                    is_string = isinstance(sample_value, str)

                if is_string:
                    signal_input.value_unit_of_measure = 'string'

            if is_string != isinstance(sample_value, str):
                # noinspection PyBroadException
                try:
                    if is_string:
                        if sample_value is not None:
                            sample_value = str(sample_value)
                    else:
                        if data[column].dtype.name == 'int64':
                            sample_value = int(sample_value)
                        else:
                            sample_value = float(sample_value)
                except BaseException:
                    # Couldn't convert it, fall through to the next conditional
                    pass

            if is_string != isinstance(sample_value, str):
                if type_mismatches == 'drop':
                    continue
                elif type_mismatches == 'raise':
                    raise SPyRuntimeError('Column "%s" was detected as %s, but %s value at (%s, %s) found. Supply '
                                          'type_mismatches parameter as "drop" to ignore the sample entirely or '
                                          '"invalid" to insert an INVALID sample in its place.' %
                                          (column, 'string-valued' if is_string else 'numeric-valued',
                                           'numeric' if is_string else 'string',
                                           index, sample_value))
                else:
                    sample_value = None

            if isinstance(sample_value, np.number):
                sample_value = sample_value.item()

            if not signal_output:
                signal_output = _put_signal(signal_metadata, signal_input)

            sample_input = SampleInputV1()
            key_in_ms = index.value / 1000000
            earliest_sample_in_ms = min(key_in_ms,
                                        earliest_sample_in_ms) if earliest_sample_in_ms is not None else key_in_ms
            latest_sample_in_ms = max(key_in_ms, latest_sample_in_ms) if latest_sample_in_ms is not None else key_in_ms

            sample_input.key = index.value
            sample_input.value = sample_value
            add_samples_input.samples.append(sample_input)

            if len(add_samples_input.samples) >= session.options.push_page_size:
                if replace is not None:
                    signals_api.put_samples(id=signal_output.id,
                                            body=add_samples_input)
                else:
                    signals_api.add_samples(id=signal_output.id,
                                            body=add_samples_input)
                count += len(add_samples_input.samples)
                page_count += 1
                status.send_update(status_index, {
                    'Result': f'Pushed to {index}',
                    'Count': count,
                    'Pages': page_count,
                    'Time': _common.timer_elapsed(timer)
                })

                add_samples_input.samples = list()

    if not signal_output:
        if signal_input.value_unit_of_measure is None and not _common.present(signal_metadata, 'ID'):
            raise SPyRuntimeError(f'Column "{column}" contains no data, does not correspond to a pre-existing signal, '
                                  f'and has no Value Unit of Measure provided. Drop the column from the data '
                                  f'dataframe, or provide an ID or Value Unit of Measure for "{column}" using the '
                                  f'metadata parameter.')
        signal_output = _put_signal(signal_metadata, signal_input)

    if len(add_samples_input.samples) > 0 or replace is not None:
        if replace is not None:
            signals_api.put_samples(id=signal_output.id,
                                    body=add_samples_input)
        else:
            signals_api.add_samples(id=signal_output.id,
                                    body=add_samples_input)
        count += len(add_samples_input.samples)
        page_count += 1

    status.send_update(status_index, {
        'Result': 'Success',
        'Count': count,
        'Pages': page_count,
        'Time': _common.timer_elapsed(timer)
    })

    return earliest_sample_in_ms, latest_sample_in_ms, signal_output.id if signal_output is not None else None


def _push_condition(session: Session, condition_metadata, replace, data, status_index, status: Status):
    conditions_api = ConditionsApi(session.client)
    condition_batch_input = ConditionBatchInputV1()
    condition_input = ConditionInputV1()
    _metadata.dict_to_condition_input(condition_metadata, condition_input)
    condition_batch_input.conditions = [condition_input]
    condition_input.datasource_class = condition_metadata['Datasource Class']
    condition_input.datasource_id = condition_metadata['Datasource ID']
    items_batch_output = conditions_api.put_conditions(body=condition_batch_input)  # type: ItemBatchOutputV1
    item_update_output = items_batch_output.item_updates[0]  # type: ItemUpdateOutputV1
    if replace is not None:
        capsules_input = CapsulesOverwriteInputV1()
    else:
        capsules_input = CapsulesInputV1()
    capsules_input.capsules = list()
    capsules_input.key_unit_of_measure = 'ns'
    count = 0
    page_count = 0
    timer = _common.timer_start()
    earliest_sample_in_ms = None
    latest_sample_in_ms = None

    if replace is not None:
        pd_start, pd_end = _login.validate_start_and_end(session, replace['Start'], replace['End'])
        interval_input = IntervalV1()
        interval_input.start = pd_start
        interval_input.end = pd_end
        capsules_input.interval = interval_input

    if data is not None:
        for index, row in data.iterrows():
            capsule = CapsuleV1()
            _dict_to_capsule(row.to_dict(), capsule)
            pd_start, pd_end = _login.validate_start_and_end(session, row['Capsule Start'], row['Capsule End'])
            capsule.start = pd_start.value
            capsule.end = pd_end.value
            capsules_input.capsules.append(capsule)
            # noinspection PyTypeChecker
            key_in_ms = capsule.start / 1000000
            earliest_sample_in_ms = min(key_in_ms,
                                        earliest_sample_in_ms) if earliest_sample_in_ms is not None else key_in_ms
            # noinspection PyTypeChecker
            key_in_ms = capsule.end / 1000000
            latest_sample_in_ms = max(key_in_ms, latest_sample_in_ms) if latest_sample_in_ms is not None else key_in_ms

            if len(capsules_input.capsules) > session.options.push_page_size:
                if replace is not None:
                    conditions_api.put_capsules(id=item_update_output.item.id, body=capsules_input)
                else:
                    conditions_api.add_capsules(id=item_update_output.item.id, body=capsules_input)

                count += len(capsules_input.capsules)
                page_count += 1
                status.send_update(status_index, {
                    'Result': f'Pushed to {index}',
                    'Count': count,
                    'Pages': page_count,
                    'Time': _common.timer_elapsed(timer)
                })
                capsules_input.capsules = list()

    if len(capsules_input.capsules) > 0 or replace is not None:
        if replace is not None:
            conditions_api.put_capsules(id=item_update_output.item.id, body=capsules_input)
        else:
            conditions_api.add_capsules(id=item_update_output.item.id, body=capsules_input)
        count += len(capsules_input.capsules)
        page_count += 1

    status.send_update(status_index, {
        'Result': 'Success',
        'Count': count,
        'Pages': page_count,
        'Time': _common.timer_elapsed(timer)
    })

    return earliest_sample_in_ms, latest_sample_in_ms, item_update_output.item.id


def _dict_to_capsule(d, capsule):
    _metadata.dict_to_input(d, capsule, 'properties', {
        'Capsule Start': None,
        'Capsule End': None
    })


def _push_workbooks(session: Session, push_result_df, folder_id, workbooks, datasource, status: Status):
    for workbook in workbooks:  # type: spy.workbooks.Analysis
        if not isinstance(workbook, spy.workbooks.Analysis):
            continue

        for worksheet in workbook.worksheets:  # type: spy.workbooks.AnalysisWorksheet
            for workstep in worksheet.worksteps.values():  # type: spy.workbooks.AnalysisWorkstep
                display_items = workstep.display_items

                # CRAB-19586: Cannot convert string to float error
                # 'ID' field is sometimes assigned float dtype in display_items dataframe but cannot duplicate this
                # This should be resolved in a fix done in workbooks/_workstep.py that cast the display_items df
                # as object type but since cannot duplicate the issue, let's patch here too
                display_items['ID'] = display_items['ID'].astype(object)

                for index, display_item in display_items.iterrows():
                    if not _common.present(display_item, 'ID') or _common.get(display_item, 'Reference', False):
                        pushed_item = get_from_push_df(display_item, push_result_df)
                        display_items.at[index, 'ID'] = pushed_item['ID']

                workstep.display_items = display_items

    return spy.workbooks.push(workbooks, path=folder_id, refresh=False, include_inventory=False, datasource=datasource,
                              status=status.create_inner('Push Workbooks'), session=session)


def get_from_push_df(display_item, push_result_df):
    item_path = _common.get(display_item, 'Path')
    item_asset = _common.get(display_item, 'Asset')
    item_name = _common.get(display_item, 'Name')
    clause = (push_result_df['Asset'] == item_asset) & (push_result_df['Name'] == item_name)
    if item_path:
        clause &= (push_result_df['Path'] == item_path)
    pushed_item = push_result_df[clause]
    if len(pushed_item) == 0:
        raise SPyRuntimeError('Could not find ID for workstep with display item where\n'
                              'Path = "%s"\nAsset = "%s"\nName = "%s"' %
                              (item_path, item_asset, item_name))
    if len(pushed_item) > 1:
        raise SPyRuntimeError('Multiple IDs for workstep with display item where\n'
                              'Path = "%s"\nAsset = "%s"\nName = "%s"\n%s' %
                              (item_path, item_asset, item_name, pushed_item))
    return pushed_item.iloc[0]


def _tree_root_to_data_id_regex(workbook_id, tree_root):
    path_regex = re.escape(tree_root) + r'(\s*>>.*)?'
    return r'\[' + re.escape(workbook_id if workbook_id else EMPTY_GUID) + r'\] \{.+?\} (' + path_regex + r')'


def get_common_root(data):
    def get_path_list(row):
        path = _metadata.determine_path(row)
        name = _common.get(row, 'Name')
        if name:
            if path:
                return _common.path_string_to_list(path + ' >> ' + name)
            else:
                return _common.path_string_to_list(name)
        else:
            return list()

    # noinspection PyTypeChecker
    full_path_series = data.apply(get_path_list, axis=1) if isinstance(data, pd.DataFrame) else data

    first_full_path_list = full_path_series.iloc[0]
    if not len(first_full_path_list):
        return None
    root_name = first_full_path_list[0]
    all_roots_same = full_path_series.apply(lambda l: len(l) and l[0] == root_name).all()
    return root_name if all_roots_same else None
