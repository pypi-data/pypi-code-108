import types
from typing import List, Dict, Union, Mapping, Optional

import numpy as np
import pandas as pd

from seeq import spy
from seeq.sdk import *
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy import _push
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status


def search(query, *, all_properties=False, workbook=_common.DEFAULT_WORKBOOK_PATH, recursive=True,
           ignore_unindexed_properties=True, include_archived=False, estimate_sample_period=None, order_by=None,
           quiet=False, status=None, session: Optional[Session] = None):
    """
    Issues a query to the Seeq Server to retrieve metadata for signals,
    conditions, scalars and assets. This metadata can then be used to retrieve
    samples, capsules for a particular time range via spy.pull().

    Parameters
    ----------
    query : {str, dict, list, pd.DataFrame, pd.Series}
        A mapping of property / match-criteria pairs or a Seeq Workbench URL

        If you supply a dict or list of dicts, then the matching
        operations are "contains" (instead of "equal to").

        If you supply a DataFrame or a Series, then the matching
        operations are "equal to" (instead of "contains").

        If you supply a str, it must be the URL of a Seeq Workbench worksheet.
        The retrieved metadata will be the signals, conditions and scalars
        currently present on the Details Panel.

        'Name' and 'Description' fields support wildcard and regular expression
        (regex) matching with the same syntax as within the Data tab in Seeq
        Workbench.

        The 'Path' field allows you to query within an asset tree, where >>
        separates each level from the next. E.g.: 'Path': 'Example >> Cooling*'
        You can use wildcard and regular expression matching at any level but,
        unlike the Name/Description fields, the match must be a "full match",
        meaning that 'Path': 'Example' will match on a root asset tree node of
        'Example' but not 'Example (AF)'.

        Available options are:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        Name                Name of the item (wildcards/regex supported)
        Path                Asset tree path of the item (should not include the
                            "leaf" asset), using ' >> ' hierarchy delimiters
        Asset               Asset name (i.e., the name of the leaf asset) or ID
        Type                The item type. One of 'Signal', 'Condition',
                              'Scalar', 'Asset', 'Chart', 'Metric', 'Workbook',
                              and 'Worksheet'
        Description         Description of the item (wildcards/regex supported)
        Datasource Name     Name of the datasource
        Datasource ID       The datasource ID, which corresponds to the Id
                            field in the connector configuration
        Datasource Class    The datasource class (e.g. 'OSIsoft PI')
        Data ID             The data ID, whose format is managed by the
                            datasource connector
        Cache Enabled       True to find items where data caching is enabled
        Scoped To           The Seeq ID of a workbook such that results are
                              limited to ONLY items scoped to that workbook.
        =================== ===================================================


    all_properties : bool, default False
        True if all item properties should be retrieved. This currently makes
        the search operation much slower as retrieval of properties for an item
        requires a separate call.

    workbook : {str, None}, default 'Data Lab >> Data Lab Analysis'
        A path string (with ' >> ' delimiters) or an ID to indicate a workbook
        such that, in addition to globally-scoped items, the workbook's scoped
        items will also be returned in the results.

        If you want all items regardless of scope, use
        workbook=spy.GLOBALS_AND_ALL_WORKBOOKS

        If you want only globally-scoped items, use
        workbook=spy.GLOBALS_ONLY

        If you don't want globally-scoped items in your results, use the
        'Scoped To' field in the 'query' argument instead. (See 'query'
        argument documentation above.)

        The ID for a workbook is visible in the URL of Seeq Workbench, directly
        after the "workbook/" part.

    recursive : bool, default True
        If True, searches that include a Path entry will include items at and
        below the specified location in an asset tree. If False, then only
        items at the specified level will be returned. To get only the root
        assets, supply a Path value of ''.

    ignore_unindexed_properties : bool, default True
        If False, a ValueError will be raised if any properties are supplied
        that cannot be used in the search.

    include_archived : bool, default False
        If True, includes trashed/archived items in the output.

    estimate_sample_period : dict, default None
        A dict with the keys 'Start' and 'End'. If provided, an estimated
        sample period for all signals will be included in the output. The
        values for the 'Start' and 'End' keys must be a string that
        pandas.to_datetime() can parse, or a pandas.Timestamp. The start
        and end times are used to bound the calculation of the sample period.
        If the start and end times encompass a time range that is insufficient
        to determine the sample period, a pd.NaT will be returned.
        If the value of 'Start' is set to None, it will default to the value of
        'End' minus 1 hour. Conversely, if the value of 'End' is set to None,
        it will default to now.

    order_by : {str, list}, default None
        An optional field or list of fields used to sort the search results.
        Fields on which results can be sorted are 'ID', 'Name', and 'Description'.

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
        func                A str value of 'spy.search'
        kwargs              A dict with the values of the input parameters
                            passed to spy.search to get the output DataFrame
        status              A spy.Status object with the status of the
                            spy.search call
        =================== ===================================================

    Examples
    --------
    Search for signals with the name 'Humid' on the asset tree under
    'Example >> Cooling Tower 1', retrieving all properties on the results:

    >>> search_results = spy.search({'Name': 'Humid', 'Path': 'Example >> Cooling Tower 1'}, all_properties=True)

    To access the stored properties:
    >>> search_results.spy.kwargs
    >>> search_results.spy.status

    Search for signals that have a name that starts with 'Area' in the datasource 'Example Data' and
    determine the sample period of each signal during the month of January 2018

    >>> search_results = spy.search({
    >>>    'Name': 'Area ?_*',
    >>>    'Datasource Name': 'Example Data'
    >>> }, estimate_sample_period=dict(Start='2018-01-01', End='2018-02-01'))

    Using a pandas.DataFrame as the input:

    >>> my_items = pd.DataFrame(
    >>>     {'Name': ['Area A_Temperature', 'Area B_Compressor Power', 'Optimize' ],
    >>>      'Datasource Name': 'Example Data'})
    >>> spy.search(my_items)

    Using a URL from a Seeq Workbench worksheet:

    >>> my_worksheet_items = spy.search(
    >>> 'https://seeq.com/workbook/17F31703-F0B6-4C8E-B7FD-E20897BD4819/worksheet/CE6A0B92-EE00-45FC-9EB3-D162632DBB48')

    """
    input_args = _common.validate_argument_types([
        (query, 'query', (str, dict, list, pd.DataFrame, pd.Series)),
        (all_properties, 'all_properties', bool),
        (workbook, 'workbook', str),
        (recursive, 'recursive', bool),
        (ignore_unindexed_properties, 'ignore_unindexed_properties', bool),
        (include_archived, 'include_archived', bool),
        (estimate_sample_period, 'estimate_sample_period', dict),
        (order_by, 'order_by', (str, list)),
        (quiet, 'quiet', bool),
        (status, 'status', Status),
        (session, 'session', Session)
    ])

    status = Status.validate(status, quiet)
    session = Session.validate(session)
    _login.validate_login(session, status)

    try:
        return _search(session, query, all_properties=all_properties, workbook=workbook, recursive=recursive,
                       ignore_unindexed_properties=ignore_unindexed_properties, include_archived=include_archived,
                       estimate_sample_period=estimate_sample_period, order_by=order_by, quiet=quiet, status=status,
                       input_args=input_args)

    except KeyboardInterrupt:
        status.update('Search canceled', Status.CANCELED)


def _search(session: Session, query, *, all_properties=False, workbook=_common.DEFAULT_WORKBOOK_PATH, recursive=True,
            ignore_unindexed_properties=True, include_archived=False, estimate_sample_period=None, order_by=None,
            quiet=False, status=None, input_args=None):
    status = Status.validate(status, quiet)
    if order_by:
        order_by = _validate_order_by(order_by)

    if estimate_sample_period is not None:
        if estimate_sample_period.keys() != {'Start', 'End'}:  # strict comparison, allowing only these two keys
            raise SPyValueError(f"estimate_sample_period must have 'Start' and 'End' keys but got "
                                f"{estimate_sample_period.keys()}")
        pd_start, pd_end = _login.validate_start_and_end(session,
                                                         estimate_sample_period['Start'],
                                                         estimate_sample_period['End'])

    if not recursive and 'Path' not in query:
        raise SPyValueError("'Path' must be included in query when recursive=False")

    items_api = ItemsApi(session.client)
    trees_api = TreesApi(session.client)
    signals_api = SignalsApi(session.client)
    conditions_api = ConditionsApi(session.client)
    scalars_api = ScalarsApi(session.client)
    formulas_api = FormulasApi(session.client)

    queries: List[Union[Dict, Mapping]]
    if isinstance(query, pd.DataFrame):
        queries = query.to_dict(orient='records')
        comparison = '=='
    elif isinstance(query, pd.Series):
        queries = [query.to_dict()]
        comparison = '=='
    elif isinstance(query, list):
        queries = query
        comparison = '~='
    elif isinstance(query, str):
        worksheet = spy.utils.get_analysis_worksheet_from_url(query, include_archived, quiet=status.quiet)
        queries = worksheet.display_items.to_dict(orient='records')
        comparison = '=='
    else:
        queries = [query]
        comparison = '~='

    #
    # This function makes use of a lot of inner function definitions that utilize variables from the outer scope.
    # In order to keep things straight, all variables confined to the inner scope are prefixed with an underscore.
    #

    metadata = list()
    columns = list()
    ids = set()
    dupe_count = 0
    sample_periods = dict()

    status.df = pd.DataFrame(queries)
    status.df['Time'] = 0
    status.df['Count'] = 0
    status.df['Pages'] = 0
    status.df['Result'] = 'Queued'
    status.update('Initializing', Status.RUNNING)

    def _add_to_dict(_dict, _key, _val):
        if _key in ['Archived', 'Cache Enabled', 'Enabled', 'Unsearchable'] and isinstance(_val, str):
            _val = _val.lower() is 'true'
        _dict[_key] = _common.none_to_nan(_val)

        # We want the columns to appear in a certain order (the order we added them in) for readability
        if _key not in columns:
            columns.append(_key)

    def _add_ancestors_to_prop_dict(_ancestors, _prop_dict):
        if len(_ancestors) > 1:
            _add_to_dict(_prop_dict, 'Path',
                         _common.path_list_to_string([_a.name for _a in _ancestors[0:-1]]))
            _add_to_dict(_prop_dict, 'Asset', _ancestors[-1].name)
        elif len(_ancestors) == 1:
            _add_to_dict(_prop_dict, 'Path', np.nan)
            _add_to_dict(_prop_dict, 'Asset', _ancestors[0].name)

    def _add_to_metadata(_prop_dict):
        if _prop_dict['ID'] not in ids:
            metadata.append(_prop_dict)
            ids.add(_prop_dict['ID'])
        else:
            nonlocal dupe_count
            dupe_count += 1

    def _estimate_sample_period(_signal):
        sampling_formula = f"$signal.estimateSamplePeriod(capsule('{pd_start.isoformat()}','{pd_end.isoformat()}'))"

        formula_run_output = formulas_api.run_formula(formula=sampling_formula,
                                                      parameters=[f"signal={_signal.id}"])

        if formula_run_output.scalar.value is not None:
            sample_periods[_signal.id] = pd.to_timedelta(
                formula_run_output.scalar.value, unit=formula_run_output.scalar.uom)
        else:
            status.warn(
                f'Sample period for signal "{_signal.name}" could not be determined. '
                f'There might not be enough data for the time period {pd_start.isoformat()} to {pd_end.isoformat()}. '
                f'Modify the time period with the `estimate_start` and `estimate_end` arguments'
            )

            sample_periods[_signal.id] = pd.NaT

    def _add_all_properties(_id, _prop_dict, _get_tree=False):
        _item = items_api.get_item_and_all_properties(id=_id)  # type: ItemOutputV1
        if _get_tree:
            asset_tree_output = trees_api.get_tree(id=_id)  # type: AssetTreeOutputV1
            asset_tree_item = asset_tree_output.item  # type: ItemPreviewWithAssetsV1
            _add_ancestors_to_prop_dict(asset_tree_item.ancestors, _prop_dict)

        # Name and Type don't seem to appear in additional properties
        _add_to_dict(_prop_dict, 'Name', _item.name)
        _add_to_dict(_prop_dict, 'Type', _item.type)
        _add_to_dict(_prop_dict, 'Scoped To', _common.none_to_nan(_item.scoped_to))

        for _prop in _item.properties:  # type: PropertyOutputV1
            _add_to_dict(_prop_dict, _prop.name, _prop.value)

        if _item.type == 'CalculatedSignal':
            _signal_output = signals_api.get_signal(id=_item.id)  # type: SignalOutputV1
            _add_to_dict(_prop_dict, 'Formula Parameters', [
                '%s=%s' % (_p.name, _p.item.id if _p.item else _p.formula) for _p in _signal_output.parameters
            ])

        if _item.type == 'CalculatedCondition':
            _condition_output = conditions_api.get_condition(id=_item.id)  # type: ConditionOutputV1
            _add_to_dict(_prop_dict, 'Formula Parameters', [
                '%s=%s' % (_p.name, _p.item.id if _p.item else _p.formula) for _p in _condition_output.parameters
            ])

        if _item.type == 'CalculatedScalar':
            _scalar_output = scalars_api.get_scalar(id=_item.id)  # type: CalculatedItemOutputV1
            _add_to_dict(_prop_dict, 'Formula Parameters', [
                '%s=%s' % (_p.name, _p.item.id if _p.item else _p.formula) for _p in _scalar_output.parameters
            ])

        return _prop_dict

    workbook_id = None
    if workbook:
        if _common.is_guid(workbook):
            workbook_id = _common.sanitize_guid(workbook)
        else:
            search_query, _ = _push.create_analysis_search_query(workbook)
            search_df = spy.workbooks.search(search_query, status=status.create_inner('Find Workbook', quiet=True),
                                             session=session)
            workbook_id = search_df.iloc[0]['ID'] if len(search_df) > 0 else None
            if workbook == _common.DEFAULT_WORKBOOK_PATH and workbook_id is None:
                workbook_id = _common.GLOBALS_ONLY

    datasource_ids = dict()
    use_search_items_api = False

    for status_index in range(len(queries)):
        timer = _common.timer_start()

        current_query = queries[status_index]

        if _common.present(current_query, 'ID'):
            # If ID is specified, short-circuit everything and just get the item directly. But since this method
            # bypasses the search_items() route that would normally supply the asset ancestors, we specifically tell
            # _add_all_properties() to make the trees_api call that will fetch the ancestors if the user wants all
            # properties to be returned.
            _prop_dict = dict()
            _add_all_properties(current_query['ID'], _prop_dict, _get_tree=all_properties)

            # Still need to determine sample period for signals and have NaT for non-signal items
            if estimate_sample_period is not None:
                if 'Signal' in current_query['Type']:
                    current_signal = signals_api.get_signal(id=current_query['ID'])
                    _estimate_sample_period(current_signal)
                else:
                    sample_periods[current_query['ID']] = pd.NaT

                _add_to_dict(_prop_dict, 'Estimated Sample Period', sample_periods[current_query['ID']])

            _add_to_metadata(_prop_dict)

            status.df.at[status_index, 'Time'] = _common.timer_elapsed(timer)
            status.df.at[status_index, 'Count'] = 1
            status.df.at[status_index, 'Result'] = 'Success'
            continue

        # If the user wants a recursive search or there's no 'Path' in the query, then use the ItemsApi.search_items API
        use_search_items_api = recursive or not _common.present(current_query, 'Path')

        if not use_search_items_api and include_archived:
            # As you can see in the code below, the TreesApi.get_tree() API doesn't have the ability to request
            # archived items
            raise SPyValueError('include_archived=True can only be used with recursive searches or searches that do '
                                'not involve a Path parameter')

        allowed_properties = ['Type', 'Name', 'Description', 'Path', 'Asset', 'Datasource Class', 'Datasource ID',
                              'Datasource Name', 'Data ID', 'Cache Enabled', 'Scoped To']

        disallowed_properties = list()
        for key, value in current_query.items():
            if key not in allowed_properties:
                disallowed_properties.append(key)

        for key in disallowed_properties:
            del current_query[key]

        allowed_properties_str = '", "'.join(allowed_properties)
        if len(disallowed_properties) > 0:
            disallowed_properties_str = '", "'.join(disallowed_properties)
            message = f'The following properties are not indexed' \
                      f'{" and will be ignored" if ignore_unindexed_properties else ""}:\n' \
                      f'"{disallowed_properties_str}"\n' \
                      f'Use any of the following searchable properties and then filter further using DataFrame ' \
                      f'operations:\n"{allowed_properties_str}"'

            if not ignore_unindexed_properties:
                raise SPyValueError(message)
            else:
                status.warn(message)

        if len(current_query) == 0:
            raise SPyValueError('No recognized properties present in "query" argument. You must provide a dict or a '
                                'DataFrame with keys or columns with at least one of the following properties: \n' +
                                allowed_properties_str)

        item_types = list()
        clauses: Dict = dict()

        if _common.present(current_query, 'Type'):
            item_type_specs = list()
            if isinstance(current_query['Type'], list):
                item_type_specs.extend(current_query['Type'])
            else:
                item_type_specs.append(current_query['Type'])

            valid_types = ['StoredSignal', 'CalculatedSignal',
                           'StoredCondition', 'CalculatedCondition',
                           'StoredScalar', 'CalculatedScalar',
                           'Datasource',
                           'ThresholdMetric', 'Chart', 'Asset',
                           'Workbook', 'Worksheet']

            for item_type_spec in item_type_specs:
                if item_type_spec == 'Signal':
                    item_types.extend(['StoredSignal', 'CalculatedSignal'])
                elif item_type_spec == 'Condition':
                    item_types.extend(['StoredCondition', 'CalculatedCondition'])
                elif item_type_spec == 'Scalar':
                    item_types.extend(['StoredScalar', 'CalculatedScalar'])
                elif item_type_spec == 'Datasource':
                    item_types.extend(['Datasource'])
                elif item_type_spec == 'Metric':
                    item_types.extend(['ThresholdMetric'])
                elif item_type_spec not in valid_types:
                    raise SPyValueError(f'Type field value not recognized: {item_type_spec}\n'
                                        f'Valid types: {", ".join(valid_types)}')
                else:
                    item_types.append(item_type_spec)

            del current_query['Type']

        for prop_name in ['Name', 'Description', 'Datasource Class', 'Datasource ID', 'Data ID']:
            if prop_name in current_query and not pd.isna(current_query[prop_name]):
                clauses[prop_name] = (comparison, current_query[prop_name])

        if _common.present(current_query, 'Datasource Name'):
            datasource_name = _common.get(current_query, 'Datasource Name')
            if datasource_name in datasource_ids:
                clauses['Datasource ID'], clauses['Datasource Class'] = datasource_ids[datasource_name]
            else:
                _filters = ['Name == %s' % datasource_name]
                if _common.present(current_query, 'Datasource ID'):
                    _filters.append('Datasource ID == %s' % _common.get(current_query, 'Datasource ID'))
                if _common.present(current_query, 'Datasource Class'):
                    _filters.append('Datasource Class == %s' % _common.get(current_query, 'Datasource Class'))

                _filter_list = [' && '.join(_filters)]
                if include_archived:
                    _filter_list.append('@includeUnsearchable')

                datasource_results = items_api.search_items(filters=_filter_list,
                                                            types=['Datasource'],
                                                            limit=100000)  # type: ItemSearchPreviewPaginatedListV1

                if len(datasource_results.items) > 1:
                    raise SPyRuntimeError(
                        'Multiple datasources found that match "%s"' % datasource_name)
                elif len(datasource_results.items) == 0:
                    raise SPyRuntimeError(
                        'No datasource found that matches "%s"' % datasource_name)
                else:
                    datasource = datasource_results.items[0]  # type: ItemSearchPreviewV1
                    clauses['Datasource ID'] = ('==', items_api.get_property(id=datasource.id,
                                                                             property_name='Datasource ID').value)
                    clauses['Datasource Class'] = ('==', items_api.get_property(id=datasource.id,
                                                                                property_name='Datasource Class').value)

                datasource_ids[datasource_name] = (clauses['Datasource ID'], clauses['Datasource Class'])

            del current_query['Datasource Name']

        filters = list()
        if len(clauses.items()) > 0:
            filters.append(' && '.join([p + c + v for p, (c, v) in clauses.items()]))

        if include_archived:
            filters.append('@includeUnsearchable')

        kwargs = {
            'filters': filters,
            'types': item_types,
            'limit': session.options.search_page_size
        }

        if workbook:
            if workbook_id:
                kwargs['scope'] = workbook_id
            elif workbook != _common.DEFAULT_WORKBOOK_PATH:
                raise SPyRuntimeError('Workbook "%s" not found, or is not accessible by you' % workbook)

        if _common.present(current_query, 'Scoped To'):
            kwargs['scope'] = current_query['Scoped To']
            kwargs['filters'].append('@excludeGloballyScoped')

        if _common.present(current_query, 'Asset'):
            if _common.is_guid(_common.get(current_query, 'Asset')):
                kwargs['asset'] = _common.get(current_query, 'Asset')
            elif not _common.present(current_query, 'Path'):
                raise SPyValueError('"Path" query parameter must be present when "Asset" name parameter present')

        path_to_query = None
        if _common.present(current_query, 'Path'):
            path_to_query = current_query['Path']
            if _common.present(current_query, 'Asset'):
                path_to_query = path_to_query + ' >> ' + current_query['Asset']

        def _do_search(_offset):
            kwargs['offset'] = _offset

            if use_search_items_api:
                if 'scope' in kwargs and isinstance(kwargs['scope'], str):
                    kwargs['scope'] = [kwargs['scope']]

                if order_by:
                    kwargs['order_by'] = order_by
                return items_api.search_items(**kwargs)
            else:
                _kwargs2 = {
                    'offset': kwargs['offset'],
                    'limit': kwargs['limit']
                }

                if 'scope' in kwargs:
                    if isinstance(kwargs['scope'], list) and len(kwargs['scope']) == 1:
                        _kwargs2['scoped_to'] = kwargs['scope'][0]
                    else:
                        _kwargs2['scoped_to'] = kwargs['scope']

                if 'asset' in kwargs:
                    _kwargs2['id'] = kwargs['asset']

                    return trees_api.get_tree(**_kwargs2)
                else:
                    return trees_api.get_tree_root_nodes(**_kwargs2)

        def _iterate_over_output(_output_func, _collection_name, _action_func):
            _offset = 0
            while True:
                _output = _output_func(_offset)

                _collection = getattr(_output, _collection_name)
                # Determine sample period for all signals and have NaT for non-signal items
                if estimate_sample_period is not None:
                    for _item in _collection:
                        if 'Signal' in _item.type:
                            _estimate_sample_period(_item)
                        else:
                            sample_periods[_item.id] = pd.NaT

                status.df.at[status_index, 'Time'] = _common.timer_elapsed(timer)
                status.df.at[status_index, 'Count'] = _offset + len(_collection)
                status.df.at[status_index, 'Pages'] += 1
                status.df.at[status_index, 'Result'] = 'Querying'
                status.update('Querying Seeq Server for items', Status.RUNNING)

                for _item in _collection:
                    _action_func(_item)

                if len(_collection) != _output.limit:
                    break

                _offset += _output.limit

        def _gather_results(_actual_path_list=None):
            def _gather_results_via_item_search(_result):
                _item_search_preview = _result  # type: ItemSearchPreviewV1
                _prop_dict = dict()

                _add_to_dict(_prop_dict, 'ID', _item_search_preview.id)
                _add_ancestors_to_prop_dict(_item_search_preview.ancestors, _prop_dict)

                _add_to_dict(_prop_dict, 'Name', _item_search_preview.name)
                _add_to_dict(_prop_dict, 'Description', _item_search_preview.description)
                _add_to_dict(_prop_dict, 'Type', _item_search_preview.type)
                _uom = _item_search_preview.value_unit_of_measure if _item_search_preview.value_unit_of_measure \
                    else _item_search_preview.source_value_unit_of_measure
                _add_to_dict(_prop_dict, 'Value Unit Of Measure', _uom)
                _datasource_item_preview = _item_search_preview.datasource  # type: ItemPreviewV1
                _add_to_dict(_prop_dict, 'Datasource Name',
                             _datasource_item_preview.name if _datasource_item_preview else None)
                _add_to_dict(_prop_dict, 'Archived', _item_search_preview.is_archived)
                if all_properties:
                    _add_all_properties(_item_search_preview.id, _prop_dict)

                if estimate_sample_period is not None:
                    _add_to_dict(_prop_dict, 'Estimated Sample Period', sample_periods[_item_search_preview.id])
                _add_to_metadata(_prop_dict)

            def _gather_results_via_get_tree(_result):
                _tree_item_output = _result  # type: TreeItemOutputV1
                _prop_dict = dict()

                for _prop, _attr in [('Name', 'name'), ('Description', 'description')]:
                    if _prop not in current_query:
                        continue

                    if not _common.does_query_fragment_match(current_query[_prop],
                                                             getattr(_tree_item_output, _attr),
                                                             contains=(comparison == '~=')):
                        return

                _add_to_dict(_prop_dict, 'ID', _tree_item_output.id)
                if len(_actual_path_list) > 1:
                    _add_to_dict(_prop_dict, 'Path', _common.path_list_to_string(_actual_path_list[0:-1]))
                    _add_to_dict(_prop_dict, 'Asset', _actual_path_list[-1])
                elif len(_actual_path_list) == 1:
                    _add_to_dict(_prop_dict, 'Path', np.nan)
                    _add_to_dict(_prop_dict, 'Asset', _actual_path_list[0])

                _add_to_dict(_prop_dict, 'Name', _tree_item_output.name)
                _add_to_dict(_prop_dict, 'Description', _tree_item_output.description)
                _add_to_dict(_prop_dict, 'Type', _tree_item_output.type)
                _add_to_dict(_prop_dict, 'Value Unit Of Measure', _tree_item_output.value_unit_of_measure)
                _add_to_dict(_prop_dict, 'Archived', _tree_item_output.is_archived)

                if all_properties:
                    _add_all_properties(_tree_item_output.id, _prop_dict)

                if estimate_sample_period is not None:
                    _add_to_dict(_prop_dict, 'Estimated Sample Period', sample_periods[_tree_item_output.id])
                _add_to_metadata(_prop_dict)

            if use_search_items_api:
                _iterate_over_output(_do_search, 'items', _gather_results_via_item_search)
            else:
                _iterate_over_output(_do_search, 'children', _gather_results_via_get_tree)

        if not _common.present(current_query, 'Path'):
            # If there's no 'Path' property in the query, we can immediately proceed to the results gathering stage.
            _gather_results()
        else:
            # If there is a 'Path' property in the query, then first we have to drill down through the tree to the
            # appropriate depth so we can find the asset ID to use for the results gathering stage.

            # We define a function here so we can use recursion through the path.
            def _process_query_path_string(_remaining_query_path_string, _actual_path_list, _asset_id=None):
                _query_path_list = _common.path_string_to_list(_remaining_query_path_string)

                _query_path_part = _query_path_list[0]

                _tree_kwargs = dict()
                _tree_kwargs['limit'] = kwargs['limit']
                _tree_kwargs['offset'] = 0

                if 'scope' in kwargs:
                    if isinstance(kwargs['scope'], list) and len(kwargs['scope']) == 1:
                        _tree_kwargs['scoped_to'] = kwargs['scope'][0]
                    else:
                        _tree_kwargs['scoped_to'] = kwargs['scope']

                while True:
                    if not _asset_id:
                        _tree_output = trees_api.get_tree_root_nodes(**_tree_kwargs)  # type: AssetTreeOutputV1
                    else:
                        _tree_kwargs['id'] = _asset_id
                        _tree_output = trees_api.get_tree(**_tree_kwargs)  # type: AssetTreeOutputV1

                    for _child in _tree_output.children:  # type: TreeItemOutputV1
                        if not _asset_id:
                            # We only filter out datasource at the top level, in case the tree is mixed
                            _datasource_ok = True
                            _child_item_output = items_api.get_item_and_all_properties(
                                id=_child.id)  # type: ItemOutputV1
                            for _prop in ['Datasource Class', 'Datasource ID']:
                                if _prop in clauses:
                                    _, _val = clauses[_prop]
                                    _p_list = [_p.value for _p in _child_item_output.properties if
                                               _p.name == _prop]
                                    if len(_p_list) == 0 or _p_list[0] != _val:
                                        _datasource_ok = False

                            if not _datasource_ok:
                                continue

                        if _common.does_query_fragment_match(_query_path_part, _child.name, contains=False):
                            _actual_path_list_for_child = _actual_path_list.copy()
                            _actual_path_list_for_child.append(_child.name)
                            if len(_query_path_list) == 1:
                                kwargs['asset'] = _child.id
                                _gather_results(_actual_path_list_for_child)
                            else:
                                _process_query_path_string(_common.path_list_to_string(_query_path_list[1:]),
                                                           _actual_path_list_for_child,
                                                           _child.id)

                    if len(_tree_output.children) < _tree_kwargs['limit']:
                        break

                    _tree_kwargs['offset'] += _tree_kwargs['limit']

            if len(path_to_query) == 0:
                _gather_results(list())
            else:
                _process_query_path_string(path_to_query, list())

        status.df.at[status_index, 'Result'] = 'Success'

    if dupe_count > 0:
        if use_search_items_api:
            arg_to_use = order_by if order_by else []
            if 'ID' in arg_to_use:
                status.warn(f'{dupe_count} duplicates removed from returned DataFrame. If you used a list of '
                            f'searches, those searches may have had overlap.')
            else:
                arg_to_use.append('ID')
                status.warn(
                    f'{dupe_count} duplicates removed from returned DataFrame. Use order_by={arg_to_use} in your '
                    f'spy.search to ensure results are not missing any items.')
        else:
            status.warn(f'{dupe_count} duplicates removed from returned DataFrame.')

    status.update('Query successful', Status.SUCCESS)

    if len(columns) == 0:
        columns = ['ID', 'Type']
    output_df = pd.DataFrame(data=metadata, columns=columns)
    if order_by and not output_df.empty:
        output_df.sort_values(order_by, ignore_index=True, inplace=True)

    output_df_properties = types.SimpleNamespace(
        func='spy.search',
        kwargs=input_args,
        status=status)

    _common.put_properties_on_df(output_df, output_df_properties)

    return output_df


def _validate_order_by(order_by):
    """
    Validate and process order_by arg of spy.search
    :param order_by: {str, list}
    :return: list
    """
    # convert string order_by to a list
    if isinstance(order_by, str):
        order_by = [order_by]

    # validate order_by
    _order_fields = ['ID', 'Name', 'Description']
    invalid_fields = [x for x in order_by if x not in _order_fields]
    if len(invalid_fields) > 0:
        raise SPyValueError(
            f"Invalid order_by fields: {invalid_fields}. Search results can only be ordered on "
            f"{_order_fields} fields.")

    return order_by
