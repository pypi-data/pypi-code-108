import pandas as pd

from seeq.spy import _common, _search
from seeq.spy._errors import *
from seeq.spy._status import Status


def process_csv_data(data, status, workbook=_common.DEFAULT_WORKBOOK_PATH):
    """
    Processes a csv file into an appropriate dataframe for Tree constructor
    :param data: str
            Filename of a CSV
    :param status: spy.Status
            The status object to pass warnings to
    :param workbook: str, default 'Data Lab >> Data Lab Analysis'
            The path to a workbook (in the form of 'Folder >> Path >> Workbook Name')
            or an ID that all pushed items will be 'scoped to'. You can
            push to the Corporate folder by using the following pattern:
            '__Corporate__ >> Folder >> Path >> Workbook Name'. A Tree currently
            may not be globally scoped. These items will not be visible/searchable
            using the data panel in other workbooks.
    :return: pandas.Dataframe
    """

    status.update('Reading CSV data', Status.RUNNING)

    csv_data = None
    try:
        csv_data = pd.read_csv(data)
    except FileNotFoundError:
        message = (f"File {data} not found. Please ensure you have it in the correct working "
                   f"directory.")
        status.exception(SPyValueError(message), throw=True)
    except BaseException as e:
        message = f"Unexpected {e}, {type(e)}"
        status.exception(SPyValueError(message), throw=True)

    csv_columns = list(csv_data.columns)
    levels = [i for i in csv_columns if 'Level' in i]

    # validation
    if 'Name' not in csv_columns and 'ID' not in csv_columns:
        message = f"A 'Name' or 'ID' column is required"
        status.exception(SPyValueError(message), throw=True)

    join_column = get_complete_column_for_join(csv_data, csv_columns, status)

    if is_first_row_of_levels_columns_blank(csv_data, levels):
        message = f"All Level columns must have a value in the first row"
        status.exception(SPyValueError(message), throw=True)

    # forward fill Levels columns
    csv_data.loc[:, levels] = csv_data.loc[:, levels].ffill()

    if join_column == 'Name':
        csv_data = get_ids_by_name_from_user_input(csv_data, status, workbook=workbook)

    return csv_data


def is_first_row_of_levels_columns_blank(csv_data, levels) -> bool:
    return csv_data[levels].iloc[0].isnull().any()


def get_complete_column_for_join(csv_data, csv_columns, status):
    name_id = csv_data[[x for x in ['Name', 'ID'] if x in csv_columns]]
    join_cols = list(name_id.columns[~name_id.isnull().any()])
    join_col = None
    if len(join_cols) == 0:
        message = f"Either 'Name' or 'ID' column must be complete, without missing values."
        status.exception(SPyValueError(message), throw=True)
    elif len(join_cols) == 2:
        join_col = 'ID'
    else:
        join_col = join_cols[0]
    return join_col


def make_paths_from_levels(csv_data):
    """
    Gets the path from a series of levels columns, adds that to the
    dataframe, and removes the levels columns
    :param csv_data: pandas.Dataframe
    :return: None
    """

    def make_path(row, levels):
        path = " >> ".join([row[i] for i in levels if not is_nan_or_string_nan(row[i])])
        return path

    level_cols = [i for i in list(csv_data.columns) if 'Level' in i]
    if len(level_cols) == 0 and 'Path' in list(csv_data.columns):
        return

    elif len(level_cols) == 0:
        # there's no levels columns and no path
        raise SPyValueError(f"Levels columns or a path column must be provided")

    else:
        csv_data['Path'] = csv_data.apply(make_path, axis=1, levels=level_cols)
        csv_data.drop(columns=level_cols, inplace=True)


def is_nan_or_string_nan(item):
    if not pd.isnull(item):
        if isinstance(item, str):
            return item.lower() == "nan"
        return False
    return True


def get_ids_by_name_from_user_input(input_df, status, workbook=_common.DEFAULT_WORKBOOK_PATH):
    """
    Adds IDs from search to a dataframe, searches based on 'Name'
    :param input_df: pandas.Dataframe
    :param status: spy.Status
    :param workbook: str, default 'Data Lab >> Data Lab Analysis'
            The path to a workbook (in the form of 'Folder >> Path >> Workbook Name')
            or an ID that all pushed items will be 'scoped to'. You can
            push to the Corporate folder by using the following pattern:
            '__Corporate__ >> Folder >> Path >> Workbook Name'. A Tree currently
            may not be globally scoped. These items will not be visible/searchable
            using the data panel in other workbooks.
    :return: pandas.Dataframe
    """

    status.update('Searching for items from CSV', Status.RUNNING)

    _search_options = ['Name', 'Type']

    if 'ID' in input_df.columns:
        # rows with IDs, no search needed
        df_with_ids = input_df.dropna(subset=['ID'])

        # rows without IDs, to search by name
        df_no_ids = input_df[input_df['ID'].isnull()].copy()

    else:
        df_with_ids = pd.DataFrame()
        df_no_ids = input_df

    if 'ID' in df_no_ids.columns:
        df_no_ids.drop(columns=['ID'], inplace=True)

    # which of the options the csv has:
    search_cols = [x for x in _search_options if x in df_no_ids.columns]

    try:
        search_res = _search.search(
            df_no_ids[search_cols], order_by=["ID"], workbook=workbook, quiet=True
        )[['Name', 'ID']]
    except KeyError:
        status.warn(f"The following names did not return search results and were "
                    f"ignored: {list(df_no_ids['Name'])}")
        return df_with_ids

    # add warning for Names with multiple search results
    multiples = search_res.loc[search_res.duplicated(subset=['Name']), 'Name']
    if len(multiples) > 0:
        status.warn(f"The following names returned multiple search results, "
                    f"so the first result was used: {list(set(multiples))}")
        search_res = search_res.drop_duplicates(subset=['Name'], keep='first').reset_index(drop=True)

    # inner merge the search results with data from csv
    name_data = df_no_ids.merge(search_res, left_on='Name', right_on='Name')

    # add warning for Names without search results
    expected_names = set()
    found_names = set()
    found_names.update(name_data['Name'])
    expected_names.update(df_no_ids['Name'])
    missing_names = expected_names.difference(found_names)
    if len(missing_names) > 0:
        status.warn(f"The following names did not return search results and were "
                    f"ignored: {list(missing_names)}")

    all_data = pd.concat([name_data, df_with_ids], axis=0, ignore_index=True)

    return all_data
