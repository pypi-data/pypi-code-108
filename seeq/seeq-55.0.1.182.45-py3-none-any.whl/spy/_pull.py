import datetime
import re
import types
from collections import defaultdict
from typing import Optional

import numpy as np
import pandas as pd

from seeq import spy
from seeq.sdk import *
from seeq.spy import _common
from seeq.spy import _login
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status

ENUM_REGEX = r'ENUM{{(\d+)\|(.+?)}}'
ENUM_PATTERN = re.compile(ENUM_REGEX)


def pull(items, *, start=None, end=None, grid='15min', header='__auto__', group_by=None, shape='auto',
         capsule_properties=None, tz_convert=None, calculation=None, bounding_values=False,
         invalid_values_as=np.nan, enums_as='string', errors='raise', quiet=False, status: Status = None,
         session: Optional[Session] = None, capsules_as=None):
    """
    Retrieves signal, condition or scalar data from Seeq Server and returns it
    in a DataFrame.

    Parameters
    ----------
    items : {str, pd.DataFrame, pd.Series}
        A DataFrame or Series containing ID and Type columns that can be used
        to identify the items to pull. This is usually created via a call to
        spy.search(). Alternatively, you can supply URL of a Seeq Workbench
        worksheet as a str.

    start : {str, pd.Timestamp}
        The starting time for which to pull data. This argument must be a
        string that pandas.to_datetime() can parse, or a pandas.Timestamp.
        If not provided, 'start' will default to 'end' minus 1 hour. Note
        that Seeq will potentially return one additional row that is earlier
        than this time (if it exists), as a "bounding value" for interpolation
        purposes. If both 'start' and 'end' are not provided and items
        is a str, 'start' will default to the start of the display range
        in Seeq Trend View.

    end : {str, pd.Timestamp}
        The end time for which to pull data. This argument must be a string
        that pandas.to_datetime() can parse, or a pandas.Timestamp.
        If not provided, 'end' will default to now. Note that Seeq will
        potentially return one additional row that is later than this time
        (if it exists), as a "bounding value" for interpolation purposes.
        If both 'start' and 'end' are not provided and items is a str,
        'end' will default to the end of the display range in Seeq Trend View.

    grid : {str, 'auto', None}, default '15min'
        A period to use for interpolation such that all returned samples
        have the same timestamps. Interpolation will be applied at the server
        to achieve this. To align samples to a different time zone and/or date
        and time, append a valid time zone and/or timestamp in ISO8601,
        YYYY-MM-DD, or YYYY-MM-DDTHH:MM:SS form. If grid=None is specified,
        no interpolation will occur and each signal's samples will be returned
        untouched. Where timestamps don't match, NaNs will be present within a
        row. If grid='auto', the period used for interpolation will be the median
        of the sample periods from the 'Estimated Sample Period' column in 'items'.
        If grid='auto' and the 'Estimated Sample Period' column does not exist
        in 'items', additional queries will be made to estimate the sample period
        which could potentially impact performance for large pulls. Interpolation
        is either linear or step and is set per signal at the time of the signal's
        creation. To change the interpolation type for a given signal, change the
        signal's interpolation or use the appropriate 'calculation' argument.

    header : str default '__auto__'
        The metadata property to use as the header of each column. Common
        values would be 'ID' or 'Name'. '__auto__' concatenates Path and Name
        if they are present.

    group_by : {str, list(str)}
        The name of a column or list of columns for which to group by. Often
        necessary when pulling data across assets: When you want header='Name',
        you typically need group_by=['Path', 'Asset']

    shape : {'auto', 'samples', 'capsules'}, default 'auto'
        If 'auto', returns capsules as a time series of 0 or 1 when signals are
        also present in the items argument, or returns capsules as individual
        rows if no signals are present. 'samples' or 'capsules' forces the
        output to the former or the latter, if possible.

    capsule_properties : list(str)
        A list of capsule properties to retrieve when shape='capsules'.
        By default, if no signals are present in the items DataFrame, then all
        properties found on a capsule are automatically returned (because
        the nature of the query allows them to be returned "for free").
        Otherwise, you must provide a list of names of properties to retrieve.

    tz_convert : {str, datetime.tzinfo}
        The time zone in which to return all timestamps. If the time zone
        string is not recognized, the list of supported time zone strings will
        be returned in the exception text.

    calculation : {str, pandas.Series, pandas.DataFrame}
        When applying a calculation across assets, the 'calculation' argument
        must be a one-row DataFrame (or a Series) and the 'items' argument must
        be full of assets. When applying a calculation to a signal/condition/
        scalar, calculation must be a string with a single variable in it:
        $signal, $condition or $scalar.

    bounding_values : bool, default False
        If True, extra 'bounding values' will be returned before/after the
        specified query range for the purposes of assisting with interpolation
        to the edges of the range or, in the case of Step or PILinear
        interpolation methods, interpolating to 'now' when appropriate.

    invalid_values_as : {str, int, float}, default np.nan
        Invalid samples and scalars will appear in the returned DataFrame as
        specified in this argument. By default, invalid values will be returned
        as NaNs. Note that specifying a string for this argument (e.g,
        'INVALID') can have significant performance implications on numeric
        signals. You may wish to use a "magic" number like -999999999 if you
        want to be able to discern invalid values but preserve algorithmic
        performance.

    enums_as : {'tuple', 'string', 'numeric', None}, default 'string'
        Enumerations, also known as digital states, are numbers that have an
        associated human-readable name with meaning in the applicable domain
        (e.g., an ON or OFF machine state that is encoded as 1 or 0).
        If enums_as='string', the signal's column in the returned DataFrame
        will be a string value (e.g., 'ON' or 'OFF'). If enums_as='numeric',
        the signal's column will be an integer (e.g. 1 or 0). If enums_as='tuple',
        both the integer and string will be supplied as a tuple
        (e.g., (1, 'ON') or (0, 'OFF')).

    errors : {'raise', 'catalog'}, default 'raise'
        If 'raise', any errors encountered will cause an exception. If
        'catalog', errors will be added to a 'Result' column in the status.df
        DataFrame.

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

    capsules_as : str
        Deprecated, use shape argument instead.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the requested data. Additionally, the following
        properties are stored on the "spy" attribute of the output DataFrame:

        =================== ===================================================
        Property            Description
        =================== ===================================================
        func                A str value of 'spy.pull'
        kwargs              A dict with the values of the input parameters
                            passed to spy.pull to get the output DataFrame
        query_df            A DataFrame with the actual query made to the
                            Seeq server
        start               A pd.Timestamp with the effective start time
                            of the data pulled
        end                 A pd.Timestamp with the effective end time
                            of the data pulled
        grid                A string with the effective grid of the data
                            pulled
        tz_convert          A datetime.tzinfo of the time zone in which
                            the timestamps were returned
        status              A spy.Status object with the status of the
                            spy.pull call
        =================== ===================================================

    Examples
    --------
    Pull a list of signals and convert the timezone to another timezone

    >>> items = pd.DataFrame([{'ID': '8543F427-2963-4B4E-9825-220D9FDCAD4E', 'Type': 'CalculatedSignal'}])
    >>> my_signals = spy.pull(items=items, grid='15min', calculation='$signal.toStep()',
    >>>          start='2019-10-5T02:53:45.567Z', end='2019-10-6', tz_convert='US/Eastern')

    To access the stored properties
    >>> my_signals.spy.kwargs
    >>> my_signals.spy.query_df
    >>> my_signals.spy.start
    >>> my_signals.spy.end
    >>> my_signals.spy.grid
    >>> my_signals.spy.status.df

    Pull a list of signals with an auto-calculated grid
    >>> signals = spy.search({'Name': 'Area ?_*', 'Datasource Name': 'Example Data'},
    >>>                        estimate_sample_period=dict(Start='2018-01-01T00:00:00Z',
    >>>                        End='2018-01-01T12:00:00Z'))
    >>> spy.pull(signals,
    >>>          start='2018-01-01T00:00:00Z',
    >>>          end='2018-01-01T23:00:00Z',
    >>>          grid='auto')

    Pull a list of signals, conditions or scalars from a Seeq worksheet with an auto-calculated grid
    >>> my_worksheet_items = spy.pull(
    >>> 'https://seeq.com/workbook/17F31703-F0B6-4C8E-B7FD-E20897BD4819/worksheet/CE6A0B92-EE00-45FC-9EB3-D162632DBB48',
    >>>  grid='auto')

    Pull a list of capsules

    >>> compressor_on_high = spy.search({'Name': 'Compressor Power on High', 'Workbook': 'Folder 1 >> Workbook 8'})
    >>> spy.pull(compressor_on_high, start='2019-01-01T04:00:00Z', end='2019-01-09T02:00:00Z')

    Pull a list of capsules but apply a condition function in formula first

    >>> comp_high = spy.search({'Name': 'Compressor Power on High', 'Workbook': 'Folder 1 >> Workbook 8'})
    >>> spy.pull(comp_high, start='2019-01-01', end='2019-01-09', calculation='$condition.setMaximumDuration(1d)')

    Pull capsules as a binary signal at the specified grid. 1 when a capsule is
    present, 0 otherwise

    >>> comp_high = spy.search({'Name': 'Compressor Power on High', 'Workbook': 'Folder 1 >> Workbook 8'})
    >>> spy.pull(comp_high, start='2019-01-01T00:00:00Z', end='2019-01-01T12:00:00Z', shape='samples', grid='1h')

    Pull a scalar

    >>> compressor_power_limit = spy.push(
    >>>     metadata=pd.DataFrame(
    >>>         [{ 'Name': 'Compressor Power Limit', 'Type': 'Scalar', 'Formula': '50kW' }]), errors='raise')
    >>> spy.pull(compressor_power_limit)

    Apply a calculation to a signal using the 'calculation' argument

    >>> signal_with_calc = spy.search({'Name': 'Area A_Temperature', 'Datasource Name': 'Example Data'})
    >>> spy.pull(signal_with_calc,
    >>>          start='2019-01-01T00:00:00',
    >>>          end='2019-01-01T03:00:00',
    >>>          calculation='$signal.aggregate(average(), hours(), startKey())', grid=None)

    Convert a linearly interpolated signal into a step interpolated signal
    using the 'calculation' argument:

    >>> items = pd.DataFrame([{'ID': '8543F427-2963-4B4E-9825-220D9FDCAD4E', 'Type': 'CalculatedSignal'}])
    >>> pull(items=items, start='2019-10-5', end='2019-10-6', grid='15min', calculation='$signal.toStep()')

    Interpolate data using the pandas.DataFrame.interpolate method with a
    second order polynomial, with the signal name as the header. Warning:
    pandas.interpolate can be considerably slower than Seeq's interpolation
    functions for large datasets, especially when using complex interpolation
    methods

    >>> search_df = pd.concat((spy.search({'ID': '6A5E44D4-C6C5-463F-827B-474AB051B2F5'}),
    >>>                        spy.search({'ID': '937449C1-16E5-4E20-AC2E-632C5CECC24B'})), ignore_index=True)
    >>> data_df = pull(search_df, grid=None, start='2019-10-5', end='2019-10-6', header='Name')
    >>> data_df.interpolate(method='quadratic')
    """

    # bringing this up here so that the error is visible before validating arguments
    if capsules_as is not None:
        raise SPyValueError("capsules_as argument is deprecated. Use the following instead:\n"
                            "capsules_as='signal'   -> shape='samples'\n"
                            "capsules_as='capsules' -> shape='capsules'")

    # noinspection PyUnresolvedReferences
    input_args = _common.validate_argument_types([
        (items, 'items', (str, pd.DataFrame, pd.Series)),
        (start, 'start', (str, pd.Timestamp, datetime.date)),
        (end, 'end', (str, pd.Timestamp, datetime.date)),
        (grid, 'grid', str),
        (header, 'header', str),
        (group_by, 'group_by', (str, list)),
        (shape, 'shape', str),
        (capsule_properties, 'capsule_properties', list),
        (tz_convert, 'tz_convert', (str, datetime.tzinfo)),
        (calculation, 'calculation', (str, pd.DataFrame, pd.Series)),
        (bounding_values, 'bounding_values', bool),
        (invalid_values_as, 'invalid_values_as', (str, int, float)),
        (errors, 'errors', str),
        (quiet, 'quiet', bool),
        (status, 'status', Status),
        (session, 'session', Session),
        (capsules_as, 'capsules_as', type(None)),
        (enums_as, 'enums_as', str)
    ])

    status = Status.validate(status, quiet)
    session = Session.validate(session)
    _login.validate_login(session, status)

    _common.validate_timezone_arg(tz_convert)
    _common.validate_errors_arg(errors)

    if enums_as is not None and enums_as not in ['tuple', 'string', 'numeric']:
        raise SPyValueError("enums_as argument must be either 'tuple', 'string', 'numeric' or None")

    if isinstance(items, str):
        # if `items` is a worksheet URL, get the actual items from the worksheet and overwrite `items` as a DataFrame
        worksheet = spy.utils.get_analysis_worksheet_from_url(items, quiet=status.quiet)
        items = spy.search(worksheet.display_items[['ID', 'Type']], all_properties=True, quiet=status.quiet,
                           session=session)
        if start is None and end is None:
            start = worksheet.display_range['Start']
            end = worksheet.display_range['End']

    if invalid_values_as is None:
        raise SPyValueError('invalid_values_as cannot be None (because Pandas treats it the same as NaN)')

    _common.validate_unique_dataframe_index(items, 'items')

    if 'ID' not in items or 'Type' not in items:
        raise SPyValueError('items DataFrame must include "ID" column and "Type" column')

    if isinstance(calculation, pd.DataFrame):
        if len(calculation) != 1:
            raise SPyValueError("When applying a calculation across assets, calculation argument must be a one-row "
                                "DataFrame, or a Series. When applying a calculation to a signal/condition/scalar, "
                                'calculation must be a string with a signal variable in it: $signal, $condition or '
                                '$scalar.')

        calculation = calculation.iloc[0]

    if isinstance(items, pd.Series):
        items = pd.DataFrame().append(items)

    if shape not in ['auto', 'capsules', 'samples']:
        raise SPyValueError("shape must be one of 'auto', 'capsules', 'samples'")

    if capsule_properties is not None and not isinstance(capsule_properties, list):
        raise SPyValueError("capsules_properties must be a list of strings (capsule property names)")

    if group_by:
        if isinstance(group_by, str):
            group_by = [group_by]
        if not isinstance(group_by, list):
            raise SPyValueError('group_by argument must be a str or list(str)')
        if not all(col in items.columns for col in group_by):
            raise SPyValueError('group_by columns %s not present in query DataFrame' % group_by)

    pd_start, pd_end = _login.validate_start_and_end(session, start, end)

    if tz_convert is None:
        # Return the results in the timezone of the start date so that the timestamps tend to make sense to the user
        tz_convert = pd_start.tz

    status_columns = [c for c in ['ID', 'Path', 'Asset', 'Name'] if c in items]

    status.df = items[status_columns].copy()
    status.df['Time'] = 0
    status.df['Count'] = 0
    status.df['Pages'] = 0
    status.df['Result'] = 'Pulling'

    query_df = items  # type: pd.DataFrame
    output = types.SimpleNamespace(df=pd.DataFrame())
    at_least_one_signal = len(query_df[query_df['Type'].str.endswith('Signal')]) > 0
    at_least_one_asset = len(query_df[query_df['Type'].str.endswith('Asset')]) > 0
    calculation_is_signal = False

    if at_least_one_asset:
        if calculation is None or not isinstance(calculation, (pd.Series, pd.DataFrame)):
            raise SPyRuntimeError('To pull data for an asset, you must provide a "calculation" argument whose '
                                  'value is the metadata of a calculation that is based on a single asset.')

        calculation_series = calculation if isinstance(calculation, pd.Series) else calculation.iloc[0]
        calculation_is_signal = calculation_series['Type'].endswith('Signal')

    if shape == 'auto':
        shape = 'samples' if at_least_one_signal or (at_least_one_asset and calculation_is_signal) else 'capsules'

    # The lifecycle of a pull is several phases. We pull signals before conditions so that, if the conditions are
    # being represented as samples, we have timestamps to map to. Scalars are last because they need to be constant
    # for all rows, and then there is a final step where we re-organize the columns to match the input order as best
    # we can.
    phases = ['signals', 'conditions', 'scalars', 'final']
    if shape == 'capsules':
        phases.remove('signals')

    placeholder_item_name = '__placeholder__'
    if shape == 'samples' and (not at_least_one_signal or (at_least_one_asset and not calculation_is_signal)):
        # If we're trying to pull a Condition as a Signal, we need a set of timestamps to use. So the user has to
        # specify a grid and then we create and pull a constant signal just to generate timestamps to which we'll
        # map the condition's 1s and 0s.

        if grid is None or grid == 'auto':
            raise SPyRuntimeError(
                "Pull cannot include conditions when no signals are present with shape='samples' and grid=%s" %
                ('None' if grid is None else f"'{grid}'"))

        row_result = _pull_signal(session, '0.toSignal(%s)' % grid, list(), placeholder_item_name,
                                  placeholder_item_name, pd_start, pd_end, tz_convert)

        output.df = row_result.result

    if grid == 'auto':
        grid = estimate_auto_grid(session, query_df, pd_start, pd_end, status)

    status.update('Pulling data from %s to %s' % (pd_start, pd_end), Status.RUNNING)
    # This dictionary is from item ID to a list of columns, which we use during the final phase to order the columns
    # in the output DataFrame. Each type of pull adds additional entries to this dictionary.
    column_names = dict()

    # This list is assembled during the final phase by going back through all the input rows and adding columns that
    # correspond to the item IDs for those rows.
    final_column_names = list()

    for phase in phases:
        status.update(f'Pulling from <strong>{pd_start}</strong> to <strong>{pd_end}</strong>', Status.RUNNING)

        index_to_use = output.df.index
        for row_index, row in query_df.iterrows():
            # noinspection PyBroadException
            try:
                if group_by and isinstance(output.df.index, pd.MultiIndex):
                    # When we're doing a group_by, then the output DataFrame may have a MultiIndex as a
                    # result of some activity that has already happened. We need to pare down the output
                    # DataFrame to the rows that should be affected by the next action, which are all the
                    # existing rows that match the current row's group_by cells.
                    index_query = ' and '.join([("%s == '%s'" % (g, row[g])) for g in group_by])
                    index_to_use = output.df.query(index_query).index.levels[0]

                # _process_query_row was broken out into a function mostly to regain some indentation
                # space. It's only ever called from this spot. That's why it has a ton of parameters.
                job = _process_query_row(session, at_least_one_signal, calculation, shape, capsule_properties, grid,
                                         header, query_df, index_to_use, row_index, pd_start, pd_end, phase, status,
                                         tz_convert, bounding_values, invalid_values_as, column_names,
                                         final_column_names, enums_as)

                def _on_success(_row_index, _job_result):
                    _item_row = query_df.loc[_row_index]
                    _row_result: RowResult = _job_result
                    _join_df = _row_result.result
                    column_names.update(_row_result.column_names)
                    if shape == 'samples':
                        if group_by is None:
                            _item_name = _join_df.columns[0]
                            if _item_name in output.df.columns:
                                raise SPyRuntimeError(
                                    f'Column headers not unique. 2+ instances of "{_item_name}" found. Use header="ID" '
                                    'to guarantee uniqueness, or alternatively try group_by=["Path", "Asset"] '
                                    'if you are using an asset tree.')
                        else:
                            for group_column in group_by:
                                _join_df[group_column] = _item_row[group_column]

                            _join_df.set_index(group_by, inplace=True, append=True)

                    if list(output.df.columns) == [placeholder_item_name]:
                        # Get rid of the placeholder column because it's no longer necessary and it'll screw
                        # things up when we're merging the partial results
                        output.df = pd.DataFrame()

                    if len(output.df) == 0:
                        existing_columns = output.df.columns
                        output.df = _join_df
                        for existing_column in existing_columns:
                            output.df[existing_column] = np.nan
                    else:
                        if shape == 'capsules':
                            # When the shape of the output is capsules, it's effectively just a long
                            # DataFrame with all of the results appended one after the other. The user can
                            # then choose to sort by one of the columns if they would like.
                            output.df = output.df.append(_join_df)
                        else:
                            # combine_first has the effect of adding the set of columns from join_df and
                            # merging the indices, adding NaNs anywhere there are cells from one DataFrame
                            # that don't match an index entry from another.
                            output.df = output.df.combine_first(_join_df)

                if job:
                    status.add_job(row_index, job, _on_success)

            except BaseException as e:
                _common.raise_or_catalog(errors, status=status, index=row_index, e=e)

        status.execute_jobs(session, errors)

    status.update(f'Pull successful from <strong>{pd_start}</strong> to <strong>{pd_end}</strong>', Status.SUCCESS)

    # Ensures that the order of the columns matches the order in the metadata
    output.df = output.df[final_column_names]

    output_df_properties = types.SimpleNamespace(
        func='spy.pull',
        kwargs=input_args,
        query_df=query_df,
        start=pd_start,
        end=pd_end,
        grid=grid,
        tz_convert=tz_convert,
        status=status)

    _common.put_properties_on_df(output.df, output_df_properties)

    return output.df


def _process_query_row(session: Session, at_least_one_signal, calculation, shape, capsule_properties, grid, header,
                       query_df, index_to_use, row_index, pd_start, pd_end, phase, status: Status, tz_convert,
                       bounding_values, invalid_values_as, column_names, final_column_names, enums_as):
    # _process_query_row was broken out into a function mostly to regain some indentation
    # space from the main pull() function. It's only ever called from one spot. That's why it has a ton of parameters.

    items_api = ItemsApi(session.client)

    row = query_df.loc[row_index]

    if phase == 'signals' and not _common.present(row, 'ID'):
        status.df.at[row_index, 'Result'] = 'No "ID" column - skipping'
        return None

    item_id, item_name, item_type = _get_item_details(session, header, row)

    calculation_to_use = calculation
    if item_type == 'Asset':
        # If we're pulling assets, then we're actually pulling a calculated item (signal, condition or scalar) that
        # has been swapped to that asset. So use the swap API to find the appropriate item and then use that item's
        # ID instead of the asset's ID. Everything else just works the same as if the user had specified the swap
        # item directly.
        swap_input = SwapInputV1()
        swap_input.swap_in = item_id
        calc_item_id, _, item_type = _get_item_details(session, header, calculation)

        item_dependency_output = items_api.get_formula_dependencies(
            id=calc_item_id)  # type: ItemDependencyOutputV1

        unique_assets = set(dep.ancestors[-1].id
                            for dep in item_dependency_output.dependencies
                            if len(dep.ancestors) > 0)

        if len(unique_assets) != 1:
            raise SPyRuntimeError('To pull data for an asset, the "calculate" parameter must be a calculated '
                                  'item that involves only one asset.')

        swap_input.swap_out = unique_assets.pop()

        swapped_item = items_api.find_swap(id=calc_item_id, body=[swap_input])  # type: ItemPreviewV1

        item_id = swapped_item.id

        # Don't try to apply a calculation later, we've already done it via our swap activity
        calculation_to_use = None

    if phase == 'signals' and \
            'Signal' not in item_type and 'Condition' not in item_type and 'Scalar' not in item_type:
        status.df.at[row_index, 'Result'] = 'Not a Signal, Condition or Scalar - skipping'
        return None

    if phase == 'signals' and 'Signal' in item_type:
        parameters = ['signal=%s' % item_id]
        if calculation_to_use is not None:
            formula = calculation_to_use
        else:
            formula = '$signal'

        if grid:
            formula = 'resample(%s, %s)' % (formula, grid)

        return (_pull_signal, session, formula, parameters, item_id, item_name, pd_start, pd_end, tz_convert,
                status, row_index, bounding_values, invalid_values_as, enums_as)

    elif phase == 'conditions' and 'Condition' in item_type:
        return (_pull_condition, session, shape, capsule_properties, calculation_to_use, item_id, item_name, header,
                pd_start, pd_end, tz_convert, row_index, index_to_use, query_df, at_least_one_signal, status)

    elif phase == 'scalars' and 'Scalar' in item_type:
        parameters = ['scalar=%s' % item_id]
        if calculation_to_use is not None:
            formula = calculation_to_use
        else:
            formula = '$scalar'

        return (_pull_scalar, session, formula, parameters, row_index, item_id, item_name, index_to_use,
                invalid_values_as, status)

    elif phase == 'final':
        # Iterate over all the column names that the _pull_xxxx functions added to the DataFrame and put them in an
        # ordered list. This code forces the output DataFrame to be consistent even if the timing of completions is
        # different from run to run.
        if item_id in column_names:
            for column_name in column_names[item_id]:
                if column_name not in final_column_names:
                    final_column_names.append(column_name)

    return None


def _convert_column_timezone(ts_column, tz):
    ts_column = ts_column.tz_localize('UTC')
    return ts_column.tz_convert(tz) if tz else ts_column


def _pull_condition(session: Session, shape, capsule_properties, calculation_to_use, item_id, item_name, header,
                    pd_start, pd_end, tz, row_index, index_to_use, query_df,
                    at_least_one_signal, status: Status):
    result_df = pd.DataFrame(index=index_to_use)
    column_names = dict()

    # noinspection PyBroadException
    timer = _common.timer_start()
    capsule_count = 0
    current_start = pd_start.value
    offset = 0
    page_count = 0
    indices_to_update = {row_index}

    def _update_status_rows(_message, _capsule_count, _page_count):
        for _row_index_to_update in indices_to_update:
            status.send_update(_row_index_to_update, {
                'Result': _message,
                'Count': _capsule_count,
                'Pages': _page_count,
                'Time': _common.timer_elapsed(timer)
            })

    while True:
        # When we want capsule summary statistics, fetch as a capsule table
        if shape == 'capsules' and at_least_one_signal:
            if calculation_to_use is not None:
                raise SPyRuntimeError("If shape='capsules' and at least one signal is present, calculation "
                                      "argument cannot be supplied")

            this_capsule_count, next_start, result_df = \
                _pull_condition_as_a_table(session, capsule_properties, current_start, query_df, item_id, item_name,
                                           header, offset, pd_end, tz, result_df, column_names, indices_to_update)
        else:
            this_capsule_count, next_start, result_df = _pull_condition_via_formula_api(
                session, calculation_to_use, shape, capsule_properties, current_start,
                index_to_use, item_id, item_name, offset, pd_end, tz, result_df, column_names)

        # Note that capsule_count here can diverge from the exact count in the output due to pagination
        capsule_count += this_capsule_count

        page_count += 1

        if this_capsule_count < session.options.pull_page_size:
            break

        if next_start == current_start:
            # This can happen if the page is full of capsules that all have the same start time
            offset += session.options.pull_page_size
        else:
            offset = 0

        current_start = next_start

        _update_status_rows(f'Pulling {_common.convert_to_timestamp(current_start, tz)}', capsule_count, page_count)

    _update_status_rows(f'Success', capsule_count, page_count)

    return RowResult(row_index, column_names, result_df)


def _is_capsule_dupe(result_df, item_name, pd_capsule_start, pd_capsule_end):
    return 'Condition' in result_df and \
           'Capsule Start' in result_df and \
           'Capsule End' in result_df and \
           len(result_df.loc[(result_df['Condition'] == item_name) &
                             (result_df['Capsule Start'] == pd_capsule_start) &
                             (result_df['Capsule End'] == pd_capsule_end)])


def _pull_condition_via_formula_api(session: Session, calculation_to_use, shape, capsule_properties, current_start,
                                    index_to_use, item_id, item_name, offset, pd_end, tz, result_df,
                                    column_names):
    formulas_api = FormulasApi(session.client)
    parameters = ['condition=%s' % item_id]
    if calculation_to_use is not None:
        formula = calculation_to_use
    else:
        formula = '$condition'

    formula_run_output, _, http_headers = formulas_api.run_formula_with_http_info(
        formula=formula,
        parameters=parameters,
        start='%d ns' % current_start,
        end='%d ns' % pd_end.value,
        offset=offset,
        limit=session.options.pull_page_size)  # type: FormulaRunOutputV1

    next_start = current_start
    capsules_output = formula_run_output.capsules  # type: CapsulesOutputV1
    check_for_dupes = True
    columns = dict()
    if shape == 'samples':
        # In this case, we are creating a signal-like representation of the condition using 0s and 1s, just like the
        # Excel and OData exports.

        columns[item_name] = pd.Series(0, index_to_use)
        for capsule in capsules_output.capsules:
            pd_capsule_start = _common.convert_to_timestamp(
                capsule.start if capsule.start is not None else 0, tz)
            pd_capsule_end = _common.convert_to_timestamp(
                capsule.end if capsule.end is not None else 7258118400000000000, tz)

            # Mark Derbecker 2019-12-17:
            # I've tried a few ways of making this happen and so far this method seems to be the most efficient: Start
            # with a Series full of zeros (but with the index that corresponds to the already-existing output
            # DataFrame) and use the Series.loc[] indexer to set the values to one if they're within the capsule
            # boundary.
            columns[item_name].loc[(columns[item_name].index >= pd_capsule_start) &
                                   (columns[item_name].index <= pd_capsule_end)] = 1

            for prop in capsule.properties:  # type: ScalarPropertyV1
                # We need to create a column name that is unique for the item / property combination
                colname = '%s - %s' % (item_name, prop.name)
                if colname not in columns:
                    # Here we start with a NaN-filled series, since we're populating property values (not 1s and 0s).
                    columns[colname] = pd.Series(np.nan, index_to_use)

                # Note here that overlapping capsules with different properties will result in "last one wins"
                columns[colname].loc[(columns[colname].index >= pd_capsule_start) &
                                     (columns[colname].index <= pd_capsule_end)] = prop.value

        column_names[item_id] = list()
        for col, series in columns.items():
            result_df[col] = series
            column_names[item_id].append(col)
    else:
        # In this case, we're creating a more straightforward table where each capsule is a row, complete with item
        # properties.

        capsule_df_rows = list()
        if len(capsules_output.capsules) > 0:
            column_names[item_id] = ['Condition', 'Capsule Start', 'Capsule End', 'Capsule Is Uncertain']

        for capsule in capsules_output.capsules:  # type: CapsuleV1
            pd_capsule_start = _common.convert_to_timestamp(capsule.start, tz)
            pd_capsule_end = _common.convert_to_timestamp(capsule.end, tz)
            if check_for_dupes and _is_capsule_dupe(result_df, item_name, pd_capsule_start, pd_capsule_end):
                # This can happen as a result of pagination
                continue

            check_for_dupes = False

            capsule_dict = {
                'Condition': item_name,
                'Capsule Start': pd_capsule_start,
                'Capsule End': pd_capsule_end,
                'Capsule Is Uncertain': bool(capsule.is_uncertain)
            }

            for prop in capsule.properties:  # type: ScalarPropertyV1
                if capsule_properties is not None and prop.name not in capsule_properties:
                    continue

                capsule_dict[prop.name] = prop.value
                if prop.name not in column_names[item_id]:
                    column_names[item_id].append(prop.name)

            capsule_df_rows.append(capsule_dict)

            if not pd.isna(capsule.start) and capsule.start > next_start:
                next_start = capsule.start

        result_df = result_df.append(capsule_df_rows) if len(result_df) != 0 else pd.DataFrame(capsule_df_rows)

    return len(capsules_output.capsules), next_start, result_df


def _build_limit_fragment(offset, limit):
    start_row = offset + 1  # Table object is 1-based, not 0
    end_row = start_row + limit
    return f'.limit({start_row}, {end_row})'


def _build_stat_formula_fragment_and_update_parameters(session: Session, signals_df, header, parameters,
                                                       indices_to_update):
    signal_id_to_stats = defaultdict(list)
    for signal_index, signal_row in signals_df.iterrows():
        signal_item_id, signal_item_name, signal_item_type = _get_item_details(session, header, signal_row)
        statistic = signal_row['Statistic'] if 'Statistic' in signal_row else 'average'

        stat_formula = _common.statistic_to_aggregation_function(statistic, allow_condition_stats=False).split('(')[0]
        stat_formula = stat_formula + '()'  # Some stats come back without the parenthesis, this forces it on each
        stat_header = f'{signal_item_name} ({statistic})'

        signal_id_to_stats[signal_item_id].append((stat_formula, stat_header))
        indices_to_update.add(signal_index)

    final_fragment = ''
    stat_headers = list()
    for (variable_count, (signal_id, stat_list)) in enumerate(signal_id_to_stats.items()):
        stat_formulas, item_headers = zip(*stat_list)
        short_id = f's{variable_count}'
        parameters.append(f'{short_id}={signal_id}')
        joined_stats = ', '.join(stat_formulas)
        final_fragment += f".addStatColumn('{short_id}', ${short_id}, {joined_stats})"
        stat_headers.extend(item_headers)

    return final_fragment, parameters, stat_headers


def _build_group_segment(property_columns):
    joined_properties = ', '.join(["'%s'" % prop for prop in property_columns])
    return f'group({joined_properties})'


def _pull_condition_as_a_table(session: Session, capsule_properties, current_start, query_df, item_id, item_name,
                               header, offset, pd_end, tz, result_df, column_names, indices_to_update):
    if not isinstance(capsule_properties, list):
        capsule_properties = list()
    required_columns = ['Capsule ID', 'Original Uncertainty', 'Condition ID', 'Start', 'End']
    # place capsule sort key as the last property column
    all_property_columns = required_columns + capsule_properties + ['Capsule SortKey']

    signals_df = query_df[query_df['Type'].str.endswith('Signal')]

    formulas_api = FormulasApi(session.client)
    start = pd.Timestamp(current_start)
    start_string = start.isoformat() + 'Z'
    end_string = pd.Timestamp(pd_end.value).isoformat() + 'Z'
    parameters = ['condition=%s' % item_id]
    capsule = f"capsule('{start_string}', '{end_string}')"
    group_segment = _build_group_segment(all_property_columns)
    limit_fragment = _build_limit_fragment(offset, session.options.pull_page_size)
    property_column_fragment = f'capsuleTable({capsule}, CapsuleBoundary.Overlap, {group_segment}, $condition)'
    sort_fragment = ".sort('Capsule ID', 'inv, asc', 'Condition Id', 'asc', 'Capsule SortKey', 'asc')"
    stat_fragment, parameters, stat_headers = _build_stat_formula_fragment_and_update_parameters(
        session, signals_df, header, parameters, indices_to_update)
    formula = property_column_fragment + stat_fragment + sort_fragment + limit_fragment
    limit = session.options.pull_page_size
    formula_run_output, _, http_headers = formulas_api.run_formula_with_http_info(
        formula=formula,
        parameters=parameters,
        offset=offset,
        limit=limit)  # type: FormulaRunOutputV1

    # Construct a dictionary to map column names to column indices
    all_column_names = all_property_columns + stat_headers
    column_names_to_indexes = {all_column_names[i]: i for i in range(len(all_column_names))}

    next_start = current_start
    formula_table = formula_run_output.table.data  # type: list
    if len(formula_table) > limit:
        formula_table = formula_table[:limit]
    check_for_dupes = True
    capsule_df_rows = list()

    for row in formula_table:
        column_names[item_id] = ['Condition', 'Capsule Start', 'Capsule End', 'Capsule Is Uncertain']
        capsule_start = pd.Timestamp(row[column_names_to_indexes['Start']]).value
        capsule_end = pd.Timestamp(row[column_names_to_indexes['End']]).value
        pd_capsule_start = _common.convert_to_timestamp(capsule_start, tz)
        pd_capsule_end = _common.convert_to_timestamp(capsule_end, tz)
        if check_for_dupes and _is_capsule_dupe(result_df, item_name, pd_capsule_start, pd_capsule_end):
            # This can happen as a result of pagination
            continue

        check_for_dupes = False

        capsule_dict = {
            'Condition': item_name,
            'Capsule Start': pd_capsule_start,
            'Capsule End': pd_capsule_end,
            'Capsule Is Uncertain': row[column_names_to_indexes['Original Uncertainty']]
        }

        # capsuleSortKey divides the properties and the stat columns in returned table
        lower_bound = all_column_names.index('Capsule SortKey') + 1
        additional_columns_for_this_row = capsule_properties + all_column_names[lower_bound:]
        for column_name in additional_columns_for_this_row:
            capsule_dict[column_name] = row[column_names_to_indexes[column_name]]
            column_names[item_id].append(column_name)

        capsule_df_rows.append(capsule_dict)

        if not pd.isna(capsule_start) and capsule_start > next_start:
            next_start = capsule_end

    formula_result_df = result_df.copy().append(capsule_df_rows) if len(result_df) != 0 else pd.DataFrame(
        capsule_df_rows)

    return len(formula_table), next_start, formula_result_df


def _pull_signal(session: Session, formula, parameters, item_id, item_name, pd_start, pd_end, tz,
                 status: Status = None, row_index=None, bounding_values=False, invalid_values_as=np.nan,
                 enums_as='string'):
    formulas_api = FormulasApi(session.client)

    # noinspection PyBroadException
    series = pd.Series(dtype=object)
    timer = _common.timer_start()
    current_start = pd_start
    last_key = 0
    page_count = 0

    while True:
        start_string = '%d ns' % current_start.value
        end_string = '%d ns' % pd_end.value
        formula_run_output, status_code, http_headers = formulas_api.run_formula_with_http_info(
            formula=formula,
            parameters=parameters,
            start=start_string,
            end=end_string,
            offset=0,
            limit=session.options.pull_page_size)  # type: FormulaRunOutputV1

        if formula_run_output.samples is None:
            # noinspection PyStringFormat
            raise SPyRuntimeError('formula_run_output.samples is None.\n'
                                  'status_code: %d\nformula: %s\nparameters: %s\n'
                                  'start: %s\nend:%s\n'
                                  'formula_run_output:\n%s' %
                                  (status_code, formula, parameters,
                                   start_string, end_string,
                                   formula_run_output.__repr__()))

        series_samples_output = formula_run_output.samples  # type: GetSamplesOutputV1

        def _keep_sample(_sample_output):
            if _sample_output.key <= last_key:
                return False

            if bounding_values:
                return True

            if _sample_output.key < pd_start.value:
                return False

            if _sample_output.key > pd_end.value:
                return False

            return True

        # Filter out the samples before breaking them into timestamps/values lists. This is the fastest.
        # https://bitbucket.org/seeq12/crab/pull-requests/8872/latest-pypi-changes-up-to-seeq-module-v133/diff#comment-134308908
        filtered_samples = [sample_output for sample_output in series_samples_output.samples if
                            _keep_sample(sample_output)]
        timestamps = [sample.key for sample in filtered_samples]
        values = [_sanitize_pi_enums(sample.value, enums_as) for sample in filtered_samples]

        time_index = _convert_column_timezone(pd.DatetimeIndex(timestamps), tz)

        series = series.append(pd.Series(values, index=time_index, dtype=object))

        page_count += 1

        if len(series_samples_output.samples) < session.options.pull_page_size:
            break

        if len(series) > 0:
            last_key = series.index[-1].value

        if time_index[-1].value > current_start.value:
            current_start = time_index[-1]

        if status is not None:
            status.send_update(row_index, {
                'Result': f'Pulling: {current_start}',
                'Count': len(series),
                'Pages': page_count,
                'Time': _common.timer_elapsed(timer)
            })

    series = series.fillna(invalid_values_as)

    if status is not None:
        status.send_update(row_index, {
            'Result': 'Success',
            'Count': len(series),
            'Pages': page_count,
            'Time': _common.timer_elapsed(timer)
        })

    return RowResult(row_index, {item_id: [item_name]}, pd.DataFrame({item_name: series}))


def _sanitize_pi_enums(value, enums_as):
    if enums_as is None:
        return value
    if not isinstance(value, str):
        return value
    match = ENUM_PATTERN.search(value)
    if match is None:
        return value
    if enums_as == 'numeric':
        return int(match.group(1))
    if enums_as == 'string':
        return match.group(2)
    return int(match.group(1)), match.group(2)


def _pull_scalar(session: Session, formula, parameters, row_index, item_id, item_name, index_to_use, invalid_values_as,
                 status: Status):
    formulas_api = FormulasApi(session.client)
    timer = _common.timer_start()

    formula_run_output, _, http_headers = formulas_api.run_formula_with_http_info(
        formula=formula,
        parameters=parameters)  # type: FormulaRunOutputV1

    status.send_update(row_index, {'Result': 'Success', 'Count': 1, 'Time': _common.timer_elapsed(timer)})

    if len(index_to_use) == 0:
        index_to_use = pd.Series([0])

    result_df = pd.DataFrame(index=index_to_use)
    value = invalid_values_as if formula_run_output.scalar.value is None else formula_run_output.scalar.value
    result_df[item_name] = value
    return RowResult(row_index, {item_id: [item_name]}, result_df)


class RowResult:
    def __init__(self, row_index, column_names, result):
        self.row_index = row_index
        self.column_names = column_names
        self.result = result


def _get_item_details(session: Session, header, row):
    # This is a somewhat complex function that tries its best to pick a column header (item_name) for the output
    # DataFrame by either honoring the user's "header" argument or auto-picking something that makes sense.

    items_api = ItemsApi(session.client)

    item_id = _common.get(row, 'ID')

    # noinspection PyTypeChecker
    item = None

    if _common.present(row, 'Type'):
        item_type = _common.get(row, 'Type')
    else:
        item = items_api.get_item_and_all_properties(id=item_id)  # type: ItemOutputV1
        item_type = item.type

    if header.upper() == 'ID':
        item_name = item_id
    elif _common.present(row, header):
        item_name = _common.get(row, header)
    else:
        if not item:
            item = items_api.get_item_and_all_properties(id=item_id)  # type: ItemOutputV1

        item_name = ''
        if header == '__auto__' and _common.present(row, 'Path'):
            item_name = _common.get(row, 'Path') + ' >> '
            if _common.present(row, 'Asset'):
                item_name += _common.get(row, 'Asset') + ' >> '

        if header in ['__auto__', 'Name']:
            item_name += item.name
        elif header == 'Description':
            item_name += item.description
        else:
            prop = [p.value for p in item.properties if p.name == header]
            if len(prop) == 0:
                raise SPyValueError(f'header argument invalid: Property "{header}" not found')
            else:
                item_name += prop[0]

    return item_id, item_name, item_type


def estimate_auto_grid(session: Session, query_df, pd_start, pd_end, status):
    if 'Estimated Sample Period' in query_df:
        status.update('Retrieving estimated sample period from query DataFrame', Status.RUNNING)
        samplings = [x for x in query_df['Estimated Sample Period'].to_list() if not pd.isna(x)]
    else:
        status.update('Estimating sample period of each signal from %s to %s' % (pd_start, pd_end), Status.RUNNING)
        signals_df = query_df[query_df['Type'].isin(['StoredSignal', 'CalculatedSignal'])]
        samplings = list()
        formulas_api = FormulasApi(session.client)
        for signal_id in signals_df['ID']:

            sampling_formula = f"$signal.estimateSamplePeriod(capsule('{pd_start.isoformat()}','{pd_end.isoformat()}'))"

            formula_run_output = formulas_api.run_formula(formula=sampling_formula, parameters=[f"signal={signal_id}"])
            if formula_run_output.scalar.value is not None:
                samplings.append(
                    pd.to_timedelta(formula_run_output.scalar.value, unit=formula_run_output.scalar.uom))

    if len(samplings) == 0:
        raise SPyRuntimeError("Could not determine sample period for any of the signals in the query. "
                              "There might not be enough data for the time period specified")

    median = np.median(np.array(samplings))
    if isinstance(median, pd.Timedelta):
        nanoseconds = median.value
    elif isinstance(median, np.timedelta64):
        nanoseconds = median.real
    else:
        raise SPyTypeError(f"Estimated Sample Period column data type {type(median)} not recognized")

    return str(int(nanoseconds / 1_000_000)) + 'ms'
