import pandas as pd

from seeq.spy import _common, _push
from seeq.spy.assets._trees import _utils


def get_full_path(node):
    if not isinstance(_common.get(node, 'Name'), str) or len(node['Name']) == 0:
        return ''
    if isinstance(_common.get(node, 'Path'), str) and len(node['Path']) != 0:
        return f"{node['Path']} >> {node['Name']}"
    return node['Name']


def sort_by_node_path(df):
    decorate_with_full_path(df)
    df.sort_values(by='Full Path List', inplace=True, ignore_index=True)
    remove_full_path(df)


def decorate_with_full_path(df):
    """
    From the 'Path' and 'Name' columns, add a 'Full Path List' column.
    """
    df.loc[:, 'Full Path List'] = df.apply(get_full_path, axis=1).apply(_common.path_string_to_list)


def remove_full_path(df):
    """
    Remove the 'Full Path List' column.
    """
    df.drop('Full Path List', axis=1, inplace=True)


def update_path_from_full_path_list(df):
    """
    From the 'Full Path List' column, set the 'Path' column.
    """
    df['Path'] = df.apply(lambda node: _common.path_list_to_string(node['Full Path List'][:-1]), axis=1)


def trim_unneeded_paths(df, parent_full_path=None, maintain_last_shared_root=None):
    """
    Remove any leading parts of the path that are shared across all rows. Then add the parent_path back onto the
    front of the path.

    E.G. If all rows have a path of 'USA >> Texas >> Houston >> Cooling Tower >> Area {x} >> ...',
    'Cooling Tower' would become the root asset for this Tree. Then if parent_path was 'My Tree >> Cooling Tower',
    all rows would have a path 'My Tree >> Cooling Tower >> Area {x} >> ...'
    """
    if len(df) == 0:
        return df

    # Get the path of the first node. It doesn't matter which we start with since we're only removing paths that are
    # shared across ALL rows.
    decorate_with_full_path(df)
    shared_root = _push.get_common_root(df['Full Path List'])
    # Trim the path until we're left with the last universally shared node.
    while shared_root:
        trimmed_full_path_list = df['Full Path List'].apply(lambda l: l[1:])
        remaining_shared_root = _push.get_common_root(trimmed_full_path_list)
        keep_last_shared_root = True
        if parent_full_path and remaining_shared_root:
            # We only want to remove the root-most path if it is already going to be the parent (due to insert)
            parent_name = _common.path_string_to_list(parent_full_path)[-1]
            keep_last_shared_root = remaining_shared_root != parent_name
        elif parent_full_path and shared_root and isinstance(maintain_last_shared_root, bool):
            # We explicitly want to remove the last shared root so it can be replaced.
            keep_last_shared_root = maintain_last_shared_root
        if not remaining_shared_root and keep_last_shared_root:
            # We need to keep the last shared root so do not save trimmed_full_path_list
            break
        df['Full Path List'] = trimmed_full_path_list
        if 'Depth' in df:
            df['Depth'] -= 1
        shared_root = remaining_shared_root

    if parent_full_path:
        # Prepend the parent path if applicable
        parent_path_list = _common.path_string_to_list(parent_full_path)
        parent_name = parent_path_list[-1]
        if _push.get_common_root(df['Full Path List']) == parent_name:
            parent_path_list.pop()
        if parent_path_list:
            df['Full Path List'] = df['Full Path List'].apply(lambda l: parent_path_list + l)
            if 'Depth' in df:
                df['Depth'] += len(parent_path_list)
    update_path_from_full_path_list(df)
    remove_full_path(df)
    return df


def get_shared_root(full_path_series):
    """
    Returns the highest shared name in the input paths. If no such name exists, returns None
    """
    first_full_path_list = full_path_series.iloc[0]
    if not len(first_full_path_list):
        return None
    root_name = first_full_path_list[0]
    all_roots_same = full_path_series.apply(lambda l: len(l) and l[0] == root_name).all()
    return root_name if all_roots_same else None


def reify_missing_assets(df, existing_parent_path=None):
    """
    Automatically generate any assets that are referred to by path only.
    E.G. If this tree were defined using a dataframe containing only leaf signals, but with a Path column of
    'Cooling Tower >> Area {x} >> {signal}', the 'Cooling Tower' and 'Area {x}' assets would be generated.

    If existing_parent_path is provided, the reification will not occur for any existing parents.
    E.G. 'Example >> Cooling Tower >> Area {x} >> {signal}' with existing_parent_path='Example'
     would only generate 'Cooling Tower' and 'Area {x}' assets, not 'Example'.
    """
    # Store the Full Path tuples of all possible Assets to be created in a set
    full_paths = set()
    for path_list in df.apply(get_full_path, axis=1).apply(_common.path_string_to_list):
        full_paths.update([tuple(path_list[:i]) for i in range(1, len(path_list))])
    # Remove all Assets whose paths are contained in the existing_parent_path
    if existing_parent_path is not None:
        full_paths.difference_update([full_path for full_path in full_paths if
                                      _common.path_list_to_string(full_path) in existing_parent_path])
    # Create dataframe rows based on these paths, and use a single pd.merge call to update the dataframe
    new_assets = pd.DataFrame([{
        'Type': 'Asset',
        'Path': _common.path_list_to_string(full_path[:-1]),
        'Name': full_path[-1],
        'Depth': len(full_path)
    } for full_path in full_paths])
    _utils.drop_duplicate_items(new_assets)
    return _utils.upsert(df, new_assets, prefer_right=False)


def determine_path(row):
    """
    Gets the path from the Path and Asset columns
    """
    path = _common.get(row, 'Path')
    asset = _common.get(row, 'Asset')
    if not isinstance(path, str):
        path = None
    if not isinstance(asset, str):
        asset = None
    return ' >> '.join([s for s in (path, asset) if s is not None])
