import copy
import re
import types

import numpy as np
import pandas as pd

from seeq.sdk import *
from seeq.spy import _common, _login, _metadata
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy.assets._trees import _constants, _match, _path, _utils


def apply_friendly_name(df):
    if 'Friendly Name' not in df.columns or df['Friendly Name'].isnull().all():
        _common.put_properties_on_df(df, types.SimpleNamespace(modified_items=set()))
        return

    # If we are changing the names of items in a dataframe whose paths are dependent on one another, then
    # record those dependencies so we can modify paths afterwards as well
    relationships = path_relationships(df)

    modified_items = set()
    for i in df.index:
        if pd.isnull(df.loc[i, 'Friendly Name']):
            continue
        if _match.is_column_value_query(df.loc[i, 'Friendly Name']):
            new_name = _match.fill_column_values(df.loc[i], df.loc[i, 'Friendly Name'])
        else:
            new_name = df.loc[i, 'Friendly Name']
        if pd.isnull(new_name):
            continue
        df.loc[i, 'Name'] = new_name
        if _common.present(df.loc[i], 'ID'):
            modified_items.add(df.loc[i, 'ID'])

    recover_relationships(df, relationships)
    _common.put_properties_on_df(df, types.SimpleNamespace(modified_items=modified_items))


def path_relationships(df):
    """
    Return a dict of dicts indicating via integers how the paths of the input rows are dependent on one another.

    Example:
        df = pd.DataFrame([{
            'Path': 'Root', 'Name': 'Item 1'
        }, {
            'Path': 'Root >> Item 1', 'Name': 'Item 2'
        }])

        output = {
            1: { # 1 refers here to the row in df with index 1, i.e., Item 2
                1: 0 # 1 refers here to the item in Item 2's path with index 1, i.e. 'Item 1'
                     # 0 refers here to the index of Item 1's row in df
            }
        }
    """
    if len(df) == 0 or 'Name' not in df.columns:
        return None
    temp_df = df[['Name']].copy()
    temp_df['Path'] = df.apply(_path.determine_path, axis=1)
    full_paths = list(temp_df.apply(_path.get_full_path, axis=1).apply(_common.path_string_to_list))
    relationships = dict()
    # This is O(n^2) but it's not a core feature
    for i, this in enumerate(full_paths):
        if this == [''] or len(this) == 0:
            continue
        for j, other in enumerate(full_paths):
            if other == ['']:
                continue
            # If the full path "other" begins with the full path "this", then we mark that
            # the (len(this) - 1)th element in "other"'s path is equal to "this"
            if len(other) > len(this) and other[:len(this)] == this:
                if j not in relationships:
                    relationships[j] = dict()
                relationships[j][len(this) - 1] = i
    return relationships


def recover_relationships(df, relationships):
    """
    Takes a list of relationships (in the format described in _path_relationships) and modifies paths in
    df to reflect those relationships
    """
    if relationships is None:
        return
    for i, path_ref_dict in relationships.items():
        path = _path.determine_path(df.loc[i])
        path_list = _common.path_string_to_list(path) if path else []
        for j, reference in path_ref_dict.items():
            if 0 <= reference < len(df) and 0 <= j < len(path_list):
                path_list[j] = df.loc[reference, 'Name']
        df.loc[i, 'Path'] = _common.path_list_to_string(path_list)
    if 'Asset' in df.columns:
        df.drop(columns='Asset', inplace=True)


def process_properties(session: Session, df, status, existing_tree_df=None, pull_nodes=True, keep_parent_column=False):
    """
    Sanitize and pull item properties into an input dataframe. Steps in order:
    -- Pulls missing properties for items with ID provided
    -- Filters out properties not in _constants.dataframe_columns
    -- Determines tree depth
    -- Determines (if possible_tree_copy is True) if the input dataframe corresponds to an existing SPy tree
        -- If it is indeed a copy of a SPy tree, pulls in calculations from the original tree
        -- Otherwise, it converts all items with IDs into references
    -- Ensures all formula parameters are NAN or dict
    """
    df = df.reset_index(drop=True)

    df = df.apply(process_row_properties, axis=1,
                  session=session,
                  status=status,
                  pull_nodes=pull_nodes,
                  keep_parent_column=keep_parent_column)

    def _row_is_from_existing_tree(row):
        if existing_tree_df is None or not _common.present(row, 'ID'):
            return 'new'
        same_id_rows = existing_tree_df[existing_tree_df.ID.str.casefold() == row['ID'].casefold()]
        if len(same_id_rows) != 1:
            return 'new'
        if _common.present(row, 'Type') and row['Type'].casefold() != same_id_rows.Type.iloc[0].casefold():
            return 'new'
        if _common.present(row, 'Name') and row['Name'].casefold() != same_id_rows.Name.iloc[0].casefold():
            return 'modified'
        if _common.present(row, 'Path') and row['Path'].casefold() != same_id_rows.Path.iloc[0].casefold():
            return 'modified'
        return 'pre-existing'

    row_type = df.apply(_row_is_from_existing_tree, axis=1)
    modified_items = df.loc[row_type == 'modified', 'ID'] if 'ID' in df.columns else set()

    # For the nodes that originated from the pre-existing SPy tree we are modifying, we want to pull
    # pre-existing calculations directly.
    formulas_api = FormulasApi(session.client)
    df.loc[row_type == 'pre-existing', :] = df.loc[row_type == 'pre-existing', :].apply(pull_calculation, axis=1,
                                                                                        formulas_api=formulas_api)

    # For the nodes that originate from places other than the pre-existing SPy tree we are modifying,
    # we want to build references so we create and modify *copies* and not the original items.
    df.loc[row_type != 'pre-existing', :] = df.loc[row_type != 'pre-existing', :].apply(make_node_reference, axis=1,
                                                                                        session=session)

    if 'Formula Parameters' in df.columns:
        df['Formula Parameters'] = df['Formula Parameters'].apply(formula_parameters_to_dict)

    _common.put_properties_on_df(df, types.SimpleNamespace(modified_items=modified_items))

    return df


# Note that the session argument is second in this special case because we call this from pd.DataFrame.apply(),
# which requires that row is the first argument.
def process_row_properties(row, session: Session, status, pull_nodes, keep_parent_column):
    if _common.present(row, 'ID') and pull_nodes:
        new_row = pull_node(session, row['ID'])
        _utils.increment_status_df(status, pulled_items=[new_row])
    else:
        new_row = pd.Series(index=_constants.dataframe_columns, dtype='object')

    # In case that properties are specified, but IDs are given, the user-given properties
    # override those pulled from Seeq
    for prop, value in row.items():
        if prop in ['Path', 'Asset']:
            prop = 'Path'
            value = _path.determine_path(row)
        elif prop == 'Type' and _common.present(new_row, 'Type') and _utils.type_differs(value, new_row['Type']):
            new_row['ID'] = np.nan
        add_tree_property(new_row, prop, value)

    if not _common.present(new_row, 'Type') and not _common.present(new_row, 'Formula'):
        new_row['Type'] = 'Asset'

    if not _common.present(new_row, 'Path'):
        new_row['Path'] = ''
    new_row['Depth'] = new_row['Path'].count('>>') + 2 if new_row['Path'] else 1

    if keep_parent_column and _common.present(row, 'Parent'):
        new_row['Parent'] = row['Parent']

    return new_row


def make_node_reference(row, session: Session):
    row = row.copy()
    if _common.present(row, 'ID'):
        if _common.get(row, 'Type') in _constants.data_types and not is_reference(row):
            _metadata.build_reference(session, row)
        if _common.present(row, 'ID'):
            row['Referenced ID'] = row['ID']
    row['ID'] = np.nan
    return row


def is_reference(row):
    if not _common.get(row, 'Referenced ID') or not _common.get(row, 'Formula Parameters'):
        return False
    formula = _common.get(row, 'Formula')
    if formula is not None and re.match(r'^\$\w+$', formula):
        return True
    else:
        return False


def pull_calculation(row, formulas_api):
    if _common.get(row, 'Type') in _constants.calculated_types and _common.present(row, 'ID'):
        row = row.copy()
        formula_output = formulas_api.get_item(id=row['ID'])  # type: FormulaItemOutputV1
        row['Formula'] = formula_output.formula
        row['Formula Parameters'] = [
            '%s=%s' % (p.name, p.item.id if p.item else p.formula) for p in formula_output.parameters
        ]
    return row


def pull_node(session: Session, node_id):
    """
    Returns a dataframe row corresponding to the item given by node_id
    """
    items_api = _login.get_api(session, ItemsApi)

    item_output = items_api.get_item_and_all_properties(id=node_id)  # type: ItemOutputV1
    node = pd.Series(index=_constants.dataframe_columns, dtype='object')

    # Extract only the properties we use
    node['Name'] = item_output.name
    node['Type'] = item_output.type
    node['ID'] = item_output.id  # If this should be a copy, it'll be converted to 'Referenced ID' later
    for prop in item_output.properties:  # type: PropertyOutputV1
        add_tree_property(node, prop.name, prop.value)

    return node


def add_tree_property(properties, key, value):
    """
    If the property is one which is used by SPy Trees, adds the key+value pair to the dict.
    """
    if key in _constants.dataframe_columns:
        value = _common.none_to_nan(value)
        if isinstance(value, str) and key in ['Cache Enabled', 'Archived', 'Enabled', 'Unsearchable']:
            # Ensure that these are booleans. Otherwise Seeq Server will silently ignore them.
            value = (value.lower() == 'true')
        if key not in properties or not (pd.api.types.is_scalar(value) and pd.isnull(value)):
            properties[key] = value
    return properties


def formula_parameters_to_dict(formula_parameters):
    if isinstance(formula_parameters, dict) or (pd.api.types.is_scalar(formula_parameters) and pd.isnull(
            formula_parameters)):
        return formula_parameters

    if isinstance(formula_parameters, str):  # formula_parameters == 'x=2b17adfd-3308-4c03-bdfb-bf4419bf7b3a'
        # handle an empty string case
        if len(formula_parameters) == 0:
            return dict()
        else:
            formula_parameters = [formula_parameters]

    if isinstance(formula_parameters, pd.Series):
        formula_parameters = formula_parameters.tolist()

    formula_dictionary = dict()
    if isinstance(formula_parameters, list):  # formula_parameters == ['x=2b17adfd-3308-4c03-bdfb-bf4419bf7b3a', ...]
        for param in formula_parameters:  # type: str
            split_list = param.split('=')  # ['x', '2b17...']
            if len(split_list) != 2:
                raise SPyException(f'Formula Parameter: {param} needs to be in the format \'paramName=inputItem\'.')
            formula_dictionary[split_list[0].strip()] = split_list[1].strip()
    return formula_dictionary  # output == {'x': '2b17adfd-3308-4c03-bdfb-bf4419bf7b3a'}


def format_formula_parameters(df, status):
    output_df = df.copy()

    output_formula_parameters_column = pd.Series(np.nan, index=output_df.index, dtype='object')

    # Takes relative-path formula parameters and changes them to full path for the ensuing push call
    for idx, row in output_df[output_df['Formula Parameters'].notnull()].iterrows():
        formula_parameters = copy.deepcopy(row['Formula Parameters'])

        for name, item in row['Formula Parameters'].items():
            if not isinstance(item, str) or _common.is_guid(item):
                continue
            item_full_path = _path.get_full_path({'Path': row['Path'], 'Name': item})

            resolved_path = None
            for _, other_row in output_df.iterrows():
                if other_row is row:
                    continue
                if _match.is_node_match(item_full_path, other_row):
                    resolved_path = _path.get_full_path(other_row)
            if resolved_path is None:
                # Validation prevents this error from being raised
                e = SPyValueError(f"Issue resolving formula parameters for item at '{row.Path} >> "
                                  f"{row.Name}'. No matches were found for '{item_full_path}'.")
                status.exception(e, throw=True)
            formula_parameters[name] = resolved_path

        output_formula_parameters_column[idx] = formula_parameters

    output_df['Formula Parameters'] = output_formula_parameters_column
    return output_df
