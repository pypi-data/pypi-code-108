import os
from typing import Optional

import numpy as np
import pandas as pd

from seeq import spy
from seeq.spy import _common
from seeq.spy import _push
from seeq.spy._errors import *
from seeq.spy._session import Session
from seeq.spy._status import Status
from seeq.spy.assets._trees import _csv, _constants, _match, _path, _properties, _pull, _utils, _validate


class Tree:
    _dataframe = pd.DataFrame()
    _workbook = _common.DEFAULT_WORKBOOK_PATH
    _workbook_id = _common.EMPTY_GUID

    quiet = False
    errors = 'raise'
    session: Session

    def __init__(self, data, *, friendly_name=None, description=None, workbook=_common.DEFAULT_WORKBOOK_PATH,
                 datasource=None, quiet=False, errors='raise', status=None, session: Optional[Session] = None):
        """
        Utilizes a Python Class-based tree to produce a set of item definitions as
        a metadata DataFrame. Allows users to manipulate the tree using various functions.

        Parameters
        ----------
        data : {pandas.DataFrame, str}
            Defines which element will be inserted at the root.
            If an existing tree already exists in Seeq, the entire tree will be pulled recursively.
            If this tree doesn't already within the scope of the workbook, new tree elements
            will be created (by deep-copy or reference if applicable).
            The following options are allowed:
            1) A name string. If an existing tree with that name (case-insensitive) is found,
                all children will be recursively pulled in.
            2) An ID string of an existing item in Seeq. If that item is in a tree, all
                children will be recursively pulled in.
            3) spy.search results or other custom dataframes. The 'Path' column must be present
                and represent a single tree structure.
            4) A filename or relative file path to a CSV file. The CSV file should have either
                a complete Name column or a complete ID column, and should specify the tree
                path for each item either in a 'Path' column formatted as "Root >> Next Level":

                +--------------------+-----------+
                | Path               | Name      |
                +--------------------+-----------+
                | Root >> Next Level | Item_Name |
                +--------------------+-----------+

                or as a series of 'Levels' columns, e.g. "Level 1" and "Level 2" columns,
                where "Level 1" would be "Root" and "Level 2" would be "Next Level":

                +---------+------------+-----------+
                | Level 1 | Level 2    | Name      |
                +---------+------------+-----------+
                | Root    | Next Level | Item_Name |
                +---------+------------+-----------+

                'Levels' columns will be forward-filled.

        friendly_name : str, optional
            Use this specified name rather than the referenced item's original name.

        description : str, optional
            The description to set on the root-level asset.

        workbook : str, default 'Data Lab >> Data Lab Analysis'
            The path to a workbook (in the form of 'Folder >> Path >> Workbook Name')
            or an ID that all pushed items will be 'scoped to'. You can
            push to the Corporate folder by using the following pattern:
            '__Corporate__ >> Folder >> Path >> Workbook Name'. A Tree currently
            may not be globally scoped. These items will not be visible/searchable
            using the data panel in other workbooks.

        datasource : str, optional
            The name of the datasource within which to contain all the
            pushed items. By default, all pushed items will be contained in a "Seeq
            Data Lab" datasource. Do not create new datasources unless you really
            want to and you have permission from your administrator.

        quiet : bool, default False
            If True, suppresses progress output. This setting will be the default for all
            operations on this Tree. This option can be changed later using
            `tree.quiet = True` or by specifying the option for individual function calls.
            Note that when status is provided, the quiet setting of the Status object
            that is passed in takes precedent.

        errors : {'raise', 'catalog'}, default 'raise'
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. The
            option chosen here will be the default for all other operations on this Tree.
            This option can be changed later using `tree.errors = 'catalog'` or by
            specifying the option for individual function calls.

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
            (data, 'data', (pd.DataFrame, str)),
            (friendly_name, 'friendly_name', str),
            (description, 'description', str),
            (workbook, 'workbook', str),
            (datasource, 'datasource', str),
            (errors, 'errors', str),
            (quiet, 'quiet', bool),
            (status, 'status', Status),
            (session, 'session', Session)
        ])
        _common.validate_errors_arg(errors)
        self.quiet = quiet
        self.errors = errors
        self.session = Session.validate(session)
        status = Status.validate(status, quiet)

        self._workbook = workbook if workbook else _common.DEFAULT_WORKBOOK_PATH
        self._datasource = datasource
        self._find_workbook_id(quiet, status)

        # check if csv file
        if isinstance(data, str):
            ext = os.path.splitext(data)[1]
            if ext == '.csv':
                # read and process csv file
                data = _csv.process_csv_data(data, status, workbook=workbook)
                # get a path column from levels columns
                _csv.make_paths_from_levels(data)
                # data is now a pd.DataFrame and can be handled as any df

        # If friendly_name is a column value query, we will apply it to the dataframe.
        # Otherwise, we will rename the root.
        rename_root = friendly_name is not None and not (isinstance(data, pd.DataFrame) and (
                _match.is_column_value_query(friendly_name) or len(data) == 1))

        if isinstance(data, pd.DataFrame):
            if len(data) == 0:
                raise SPyValueError("A tree may not be created from a DataFrame with no rows")

            _utils.initialize_status_df(status, 'Created', 'Constructing Tree object from dataframe input.',
                                        Status.RUNNING)

            # Check user input for errors, filter if errors='catalog'
            df = _validate.validate_and_filter(self.session, data, status, errors, stage='input',
                                               error_message_header='Errors were encountered before creating tree',
                                               raise_if_all_filtered=True)

            df = df.reset_index(drop=True)

            # If the dataframe specifies a root with ID and Name corresponding to a previously pushed SPy tree,
            # then we want this object to modify the same tree rather than create a copy of it. If such a tree
            # exists, then we store its current state in existing_tree_df
            existing_tree_df = _pull.get_existing_spy_tree(self.session, df, self._workbook_id)

            if friendly_name is not None:
                if _match.is_column_value_query(friendly_name):
                    df['Friendly Name'] = friendly_name
                elif len(df) == 1:
                    df['Name'] = friendly_name
            _properties.apply_friendly_name(df)
            modified_items = df.spy.modified_items

            # Sanitize data and pull in properties of items with IDs. Make items with IDs into references unless
            # they are contained in existing_tree_df
            df = _properties.process_properties(self.session, df, status, existing_tree_df=existing_tree_df)
            modified_items.update(df.spy.modified_items)

            # Rectify paths
            df = _path.trim_unneeded_paths(df)
            df = _path.reify_missing_assets(df)

            # Pull children of items with IDs
            df = _pull.pull_all_children_of_all_nodes(self.session, df, self._workbook_id, existing_tree_df,
                                                      item_ids_to_ignore=modified_items,
                                                      status=status)
            _utils.increment_status_df(status, new_items=df)

            status_message = f"Tree successfully created from DataFrame."
            if existing_tree_df is not None:
                status_message += f' This tree modifies a pre-existing SPy-created tree with name ' \
                                  f'"{existing_tree_df.ID.iloc[0]}".'

        elif data and isinstance(data, str):
            if _common.is_guid(data):
                existing_node_id = data
            else:
                status.update(f'Searching for existing asset tree roots with name "{data}"', Status.RUNNING)
                existing_node_id = _pull.find_root_node_by_name(self.session, data, self._workbook_id, status)

            if existing_node_id:
                _utils.initialize_status_df(status, 'Created', f'Pulling existing asset tree "{data}".',
                                            Status.RUNNING)

                # Pull an existing tree. Detect whether it originated from SPy
                df = _pull.pull_tree(self.session, existing_node_id, self._workbook_id, status=status)
                _utils.increment_status_df(status, new_items=df)

                status_message = f"Recursively pulled {'SPy-created' if df.spy.spy_tree else 'existing'} " \
                                 f"asset tree."
            else:
                _utils.initialize_status_df(status, 'Created', f'Creating asset tree with new root "{data}".',
                                            Status.RUNNING)

                # Define a brand new root asset
                df = pd.DataFrame([{
                    'Type': 'Asset',
                    'Path': '',
                    'Depth': 1,
                    'Name': data,
                    'Description': description if description else np.nan
                }], columns=_constants.dataframe_columns)
                _utils.increment_status_df(status, new_items=df)

                status_message = f'No existing root found. Tree created using new root "{data}".' \
                                 f'{"" if self.session.client else " If an existing tree was expected, please log in."}'

        else:
            raise SPyTypeError("Input 'data' must be a name, name of a csv file, Seeq ID, or Metadata dataframe when "
                               "creating a Tree")

        _path.sort_by_node_path(df)
        if description:
            df.loc[0, 'Description'] = description
        if rename_root:
            df = _utils.set_name(df, friendly_name)

        # Unlike in Tree.insert(), this final validation step will catch some user errors such as including two roots
        df = _validate.validate_and_filter(self.session, df, status, errors, stage='final',
                                           error_message_header='Errors were encountered while creating tree',
                                           fatal_message='Errors were encountered while validating tree',
                                           subtract_errors_from_status=True)

        self._dataframe = df
        status.update(f'{status_message} {self.summarize(ret=True)}', Status.SUCCESS)

    def insert(self, children=None, parent=None, *, friendly_name=None, formula=None, formula_parameters=None,
               errors=None, quiet=None, status=None):
        """
        Insert the specified elements into the tree.

        Parameters
        ----------
        children : {pandas.DataFrame, str, list, Tree}, optional
            Defines which element or elements will be inserted below each parent. If an existing
            node already existed at the level in the tree with that name (case-insensitive),
            it will be updated. If it doesn't already exist, a new node will be created
            (by deep-copy or reference if applicable).
            The following options are allowed:
            1) A basic string or list of strings to create a new asset.
            2) Another SPy Tree.
            3) spy.search results or other custom dataframes.

        parent : {pandas.DataFrame, str, int, list}, optional
            Defines which element or elements the children will be inserted below.
            If a parent match is not found and non-glob/regex string or path is used,
            the parent (or entire path) will be created too.
            The following options are allowed:
            1) No parent specified will insert directly to the root of the tree.
            2) String name match (case-insensitive equality, globbing, regex, column
                values) will find any existing nodes in the tree that match.
            3) String path match, including partial path matches.
            4) ID. This can either be the actual ID of the tree.push()ed node or the
                ID of the source item.
            5) Number specifying tree level. This will add the children below every
                node at the specified level in the tree (1 being the root node).
            6) spy.search results or other custom dataframe.

        friendly_name : str, optional
            Use this specified name rather than the referenced item's original name.

        formula : str, optional
            The formula for a calculated item. The `formula` and `formula_parameters` are
            used in place of the `children` argument.

        formula_parameters : dict, optional
            The parameters for a formula.

        errors : {'raise', 'catalog'}, optional
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. This
            input will be used only for the duration of this function; it will default
            to the setting on the Tree if not specified.

        quiet : bool, optional
            If True, suppresses progress output. This input will be used only for the
            duration of this function; it will default to the setting on the Tree if
            not specified. Note that when status is provided, the quiet setting of
            the Status object that is passed in takes precedent.

        status : spy.Status, optional
            If specified, the supplied Status object will be updated as the command
            progresses. It gets filled in with the same information you would see
            in Jupyter in the blue/green/red table below your code while the
            command is executed. The table itself is accessible as a DataFrame via
            the status.df property.
        """

        _common.validate_argument_types([
            (children, 'children', (pd.DataFrame, Tree, str, list)),
            (parent, 'parent', (pd.DataFrame, list, str, int)),
            (friendly_name, 'friendly_name', str),
            (formula, 'formula', str),
            (formula_parameters, 'formula_parameters', (dict, list, str)),
            (errors, 'errors', str),
            (quiet, 'quiet', bool),
            (status, 'status', Status)
        ])
        errors = self._get_or_default_errors(errors)
        quiet = self._get_or_default_quiet(quiet)
        status = Status.validate(status, quiet)

        if children is None:
            if not friendly_name:
                e = SPyValueError('Friendly Name must be specified if no children argument is given.')
                status.exception(e, throw=True)
            else:
                children = pd.DataFrame([{
                    'Name': friendly_name
                }])

        if isinstance(children, str):
            children = [children]
        if isinstance(children, list):
            for child in children:
                if not isinstance(child, str):
                    raise SPyValueError(f'List input to children argument contained non-string data: {child}')
            children = pd.DataFrame([{'ID': child} if _common.is_guid(child) else
                                     {'Name': child} for child in children])
        elif isinstance(children, Tree):
            children = children._dataframe.copy()

        if formula:
            if 'Formula' in children.columns or 'Formula Parameters' in children.columns:
                e = SPyValueError(
                    f"Children DataFrame cannot contain a 'Formula' or 'Formula Parameters' column when inserting a "
                    f"formula.")
                status.exception(e, throw=True)
            else:
                children['Formula'] = formula
                children['Formula Parameters'] = [formula_parameters] * len(children)

        _utils.initialize_status_df(status, 'Inserted',
                                    'Processing item properties and finding children to be inserted.',
                                    Status.RUNNING)

        # Check user input for errors, filter if errors='catalog'
        children = _validate.validate_and_filter(self.session, children, status, errors, stage='input',
                                                 error_message_header='Errors were encountered in input')

        children = children.reset_index(drop=True)

        if parent is not None and 'Parent' in children.columns:
            status.exception(SPyRuntimeError('If a "Parent" column is specified in the children dataframe, then the '
                                             'parent argument of the insert() method must be None'), throw=True)

        if _match.is_column_value_query(parent):
            children['Parent'] = children.apply(_match.fill_column_values, axis=1, query=parent)
        elif 'Parent' in children.columns:
            children['Parent'] = children.apply(_match.fill_column_values, axis=1,
                                                query_column='Parent')

        if friendly_name is not None:
            if _match.is_column_value_query(friendly_name):
                children['Friendly Name'] = friendly_name
            else:
                if len(children) > 1:
                    status.exception(SPyRuntimeError(
                        'friendly_name must be a column value query when multiple children are inputted'), throw=True)
                elif len(children) == 1:
                    children['Name'] = friendly_name
        _properties.apply_friendly_name(children)

        # Sanitize data and pull in properties of items with IDs
        children = _properties.process_properties(self.session, children, status, keep_parent_column=True)

        # Pull children of items with pre-existing IDs
        children = _pull.pull_all_children_of_all_nodes(self.session, children, self._workbook_id,
                                                        status=status)

        # Pre-insertion validation. This should only validate that we didn't pull in any metrics. We use
        # errors='catalog' so that the user isn't screwed when inserting an asset with threshold metric children
        children = _validate.validate_and_filter(self.session, children, status, errors='catalog',
                                                 stage='filter_out_metrics',
                                                 error_message_header='Errors were encountered before inserting')

        def _get_children_to_add(children_df, parent_node):
            if 'Parent' in children_df.columns:
                children_to_add = children_df[
                    children_df['Parent'].apply(_match.is_node_match, node=parent_node)].copy()
            else:
                children_to_add = children_df.copy()
            parent_full_path = _path.get_full_path(parent_node)
            if 'Path' in children_df.columns and not pd.isna(children_df['Path']).all():
                # Simplify path while maintaining subtree structure
                children_to_add = _path.trim_unneeded_paths(children_to_add, parent_full_path)
                children_to_add = _path.reify_missing_assets(children_to_add, parent_full_path)
            else:
                # No path found in the input children DF. All children will be below this parent.
                children_to_add['Path'] = parent_full_path
                children_to_add['Depth'] = parent_node['Depth'] + 1
            return children_to_add

        # If 'Parent' column is given, or parent argument has column values, define the parent matcher as this column
        if 'Parent' in children.columns:
            parent_pattern = children['Parent']
        else:
            parent_pattern = parent

        # We concatenate all children to be inserted into one dataframe before
        # inserting them using a single pd.merge call
        additions = [_get_children_to_add(children, row) for _, row in self._dataframe.iterrows()
                     if _match.is_node_match(parent_pattern, row)]
        additions = pd.concat(additions, ignore_index=True) if additions else pd.DataFrame()
        # Remove duplicate items in case the user has passed duplicate information to the children parameter
        _utils.drop_duplicate_items(additions)

        _utils.increment_status_df(status, new_items=additions)

        # Merge the dataframes on case-insensitive 'Path' and 'Name' columns
        working_df = _utils.upsert(self._dataframe.copy(), additions)
        _path.sort_by_node_path(working_df)

        # If errors occur during the following validation step, they are "our fault", i.e., we inserted into the tree
        # incorrectly. We ideally want all feasible user errors to be reported before this point
        working_df = _validate.validate_and_filter(self.session, working_df, status, errors, stage='final',
                                                   error_message_header='Errors were encountered while inserting',
                                                   fatal_message='Errors were encountered while validating tree',
                                                   subtract_errors_from_status=True)
        self._dataframe = working_df

        if status.df.squeeze()['Total Items Inserted'] == 0 and status.df.squeeze()['Errors Encountered'] == 0:
            status.warn('No matching parents found. Nothing was inserted.')
        status.update(f'Successfully inserted items into the tree. {self.summarize(ret=True)}', Status.SUCCESS)

    def remove(self, elements, *, errors=None, quiet=None, status=None):
        """
        Remove the specified elements from the tree recursively.

        Parameters
        ----------
        elements : {pandas.DataFrame, str, int}
            Defines which element or elements will be removed.
            1) String name match (case-insensitive equality, globbing, regex, column
                values) will find any existing nodes in the tree that match.
            2) String path match, including partial path matches.
            3) ID. This can either be the actual ID of the tree.push()ed node or the
                ID of the source item.
            4) Number specifying tree level. This will add the children below every
                node at the specified level in the tree (1 being the root node).
            5) spy.search results or other custom dataframe.

        errors : {'raise', 'catalog'}, optional
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. This
            input will be used only for the duration of this function; it will default
            to the setting on the Tree if not specified.

        quiet : bool, optional
            If True, suppresses progress output. This input will be used only for the
            duration of this function; it will default to the setting on the Tree if
            not specified. Note that when status is provided, the quiet setting of
            the Status object that is passed in takes precedent.

        status : spy.Status, optional
            If specified, the supplied Status object will be updated as the command
            progresses. It gets filled in with the same information you would see
            in Jupyter in the blue/green/red table below your code while the
            command is executed. The table itself is accessible as a DataFrame via
            the status.df property.
        """

        _common.validate_argument_types([
            (elements, 'elements', (pd.DataFrame, str, int)),
            (errors, 'errors', str),
            (quiet, 'quiet', bool),
            (status, 'status', Status)
        ])

        errors = self._get_or_default_errors(errors)
        quiet = self._get_or_default_quiet(quiet)
        status = Status.validate(status, quiet)

        working_df = self._dataframe.copy()
        _utils.initialize_status_df(status, 'Removed', 'Removing items from tree', Status.RUNNING)

        idx = 1
        while idx < len(working_df.index):
            node = working_df.iloc[idx]
            if _match.is_node_match(elements, node):
                subtree_selector = working_df.index == idx
                subtree_selector = subtree_selector | (
                    working_df['Path'].str.casefold().str.startswith(
                        _path.get_full_path(node).casefold(), na=False)
                )

                _utils.increment_status_df(status, new_items=working_df[subtree_selector])
                working_df.drop(working_df.index[subtree_selector], inplace=True)
                working_df.reset_index(drop=True, inplace=True)
            else:
                idx += 1

        working_df = _validate.validate_and_filter(self.session, working_df, status, errors, stage='final',
                                                   error_message_header='Errors were encountered while removing',
                                                   fatal_message='Errors were encountered while validating tree')
        self._dataframe = working_df

        if status.df.squeeze()['Total Items Removed'] == 0 and status.df.squeeze()['Errors Encountered'] == 0:
            status.warn('No matches found. Nothing was removed.')
        status.update(f'Successfully removed items from the tree. {self.summarize(ret=True)}',
                      Status.SUCCESS)

    def move(self, source, destination=None, *, errors=None, quiet=None, status=None):
        """
        Move the specified elements (and all children) from one location in
        the tree to another.

        Parameters
        ----------
        source : {pandas.DataFrame, str}
            Defines which element or elements will be moved.
            1) String path match.
            2) ID. This can either be the actual ID of the tree.push()ed node or the
                ID of the source item.
            3) spy.search results or other custom dataframe.

        destination : {pandas.DataFrame, str}; optional
            Defines the new parent for the source elements.
            1) No destination specified will move the elements to just below
              the root of the tree.
            2) String path match.
            3) ID. This can either be the actual ID of the tree.push()ed node or the
                ID of the source item.
            4) spy.search results or other custom dataframe.

        errors : {'raise', 'catalog'}, optional
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. This
            input will be used only for the duration of this function; it will default
            to the setting on the Tree if not specified.

        quiet : bool, optional
            If True, suppresses progress output. This input will be used only for the
            duration of this function; it will default to the setting on the Tree if
            not specified. Note that when status is provided, the quiet setting of
            the Status object that is passed in takes precedent.

        status : spy.Status, optional
            If specified, the supplied Status object will be updated as the command
            progresses. It gets filled in with the same information you would see
            in Jupyter in the blue/green/red table below your code while the
            command is executed. The table itself is accessible as a DataFrame via
            the status.df property.
        """

        _common.validate_argument_types([
            (source, 'source', (pd.DataFrame, str)),
            (destination, 'destination', (pd.DataFrame, str)),
            (errors, 'errors', str),
            (quiet, 'quiet', bool),
            (status, 'status', Status)
        ])

        errors = self._get_or_default_errors(errors)
        quiet = self._get_or_default_quiet(quiet)
        status = Status.validate(status, quiet)

        working_df = self._dataframe.copy()
        _utils.initialize_status_df(status, 'Moved', 'Moving items in tree.', Status.RUNNING)

        # Find the destination. Fail if there is not exactly one match for the input
        destination_node = working_df[
            working_df.apply(lambda node: _match.is_node_match(destination, node), axis=1)]
        if len(destination_node) == 0:
            status.exception(SPyValueError('Destination does not match any item in the tree.'), throw=True)
        elif len(destination_node) > 1:
            matched_names = '"%s"' % '", "'.join(destination_node.head(5).apply(
                _path.get_full_path, axis=1))
            status.exception(SPyValueError(f'Destination must match a single element of the tree. Specified '
                                           f'destination matches: "{matched_names}".'), throw=True)
        elif destination_node['Type'].iloc[0] != 'Asset':
            status.exception(SPyValueError('Destination must be an asset.'), throw=True)
        destination_path = _path.get_full_path(destination_node.iloc[0])

        # Find all source items, collect all of their children, and separate all matches into discrete subtrees.
        source_selector = working_df.apply(
            lambda node: _match.is_node_match(source, node) and node['Path'] != destination_path,
            axis=1
        )
        source_tree_roots = working_df[source_selector]
        for _, row in source_tree_roots.iterrows():
            source_selector = source_selector | working_df['Path'].str.startswith(
                _path.get_full_path(row), na=False)
        if source_selector[destination_node.index[0]]:
            status.exception(SPyValueError('Source cannot contain the destination'), throw=True)
        source_nodes = working_df[source_selector]

        def _split_selection_into_subtrees(df):
            if len(df) == 0:
                return []
            initial_depth = df.iloc[0]['Depth']

            above_initial_depth = df[df['Depth'] <= initial_depth]
            if len(above_initial_depth) == 1:
                return [df.copy()]
            next_subtree_index = above_initial_depth.index[1]

            first_subtree = df[df.index < next_subtree_index]
            others = df[df.index >= next_subtree_index]
            return [first_subtree.copy()] + _split_selection_into_subtrees(others)

        source_trees = _split_selection_into_subtrees(source_nodes)

        # Change path of each subtree, collect them into a single dataframe, and wipe any previously pushed IDs
        additions = [_path.trim_unneeded_paths(subtree, parent_full_path=destination_path) for
                     subtree in source_trees]
        additions = pd.concat(additions, ignore_index=True) if additions else pd.DataFrame()
        additions['ID'] = np.nan

        _utils.increment_status_df(status, new_items=additions)

        # Drop the old items and utils.upsert the modified items
        working_df.drop(source_nodes.index, inplace=True)
        working_df = _utils.upsert(working_df, additions)
        _path.sort_by_node_path(working_df)

        working_df = _validate.validate_and_filter(self.session, working_df, status, errors, stage='final',
                                                   error_message_header='Errors were encountered after moving',
                                                   fatal_message='Errors were encountered after validation')
        self._dataframe = working_df

        if status.df.squeeze()['Total Items Moved'] == 0 and status.df.squeeze()['Errors Encountered'] == 0:
            status.warn('No matches found. Nothing was moved.')
        status.update(f'Successfully moved items within the tree. {self.summarize(ret=True)}',
                      Status.SUCCESS)

    @property
    def size(self):
        """
        Property that gives the number of elements currently in the tree.
        """
        return len(self._dataframe)

    def __len__(self):
        return self.size

    @property
    def height(self):
        """
        Property that gives the current height of the tree. This is the length
        of the longest item path within the tree.
        """
        return self._dataframe['Depth'].max()

    def items(self):
        return self._dataframe.copy()

    def count(self, item_type=None):
        """
        Count the number of elements in the tree of each Seeq type. If item_type
        is not specified, then returns a dictionary with keys 'Asset', 'Signal',
        'Condition', 'Scalar', and 'Unknown'. If item_type is specified, then
        returns an int.

        Parameters
        ----------
        item_type : {'Asset', 'Signal', 'Condition', 'Scalar', 'Uncompiled Formula'}, optional
            If specified, then the method will return an int representing the
            number of elements with Type item_type. Otherwise, a dict will be
            returned.
        """

        simple_types = ['Asset', 'Signal', 'Condition', 'Scalar', 'Uncompiled Formula']
        if item_type:
            if not isinstance(item_type, str) or item_type.capitalize() not in (simple_types + ['Formula',
                                                                                                'Uncompiled']):
                raise SPyValueError(f'"{item_type}" is not a valid node type. Valid types are: '
                                    f'{", ".join(simple_types)}')
            if item_type in ['Uncompiled Formula', 'Uncompiled', 'Formula']:
                return sum(pd.isnull(self._dataframe['Type']) | (self._dataframe['Type'] == ''))
            else:
                return sum(self._dataframe['Type'].str.contains(item_type.capitalize(), na=False))

        def _simplify_type(t):
            if not pd.isnull(t):
                for simple_type in simple_types:
                    if simple_type in t:
                        return simple_type
            return 'Uncompiled Formula'

        return self._dataframe['Type'] \
            .apply(_simplify_type) \
            .value_counts() \
            .to_dict()

    def summarize(self, ret=False):
        """
        Generate a human-readable summary of the tree.

        Parameters
        ----------
        ret : bool, default False
            If True, then this method returns a string summary of the tree. If
            False, then this method prints the summary and returns nothing.
        """
        counts = self.count()

        def _get_descriptor(k, v):
            singular_descriptors = {
                key: key.lower() if key != 'Uncompiled Formula' else 'calculation whose type has not '
                                                                     'yet been determined'
                for key in counts.keys()
            }
            plural_descriptors = {
                key: f'{key.lower()}s' if key != 'Uncompiled Formula' else 'calculations whose types have not '
                                                                           'yet been determined'
                for key in counts.keys()
            }
            if v == 1:
                return singular_descriptors[k]
            else:
                return plural_descriptors[k]

        nonzero_counts = {k: v for k, v in counts.items() if v != 0}
        if len(nonzero_counts) == 1:
            count_string = ''.join([f'{v} {_get_descriptor(k, v)}' for k, v in nonzero_counts.items()])
        elif len(nonzero_counts) == 2:
            count_string = ' and '.join([f'{v} {_get_descriptor(k, v)}' for k, v in nonzero_counts.items()])
        elif len(nonzero_counts) > 2:
            count_string = ', '.join([f'{v} {_get_descriptor(k, v)}' for k, v in nonzero_counts.items()])
            last_comma = count_string.rfind(',')
            count_string = count_string[:last_comma + 2] + 'and ' + count_string[last_comma + 2:]
        else:
            return

        root_name = self._dataframe.iloc[0]['Name']

        summary = f'The tree "{root_name}" has height {self.height} and contains {count_string}.'

        if ret:
            return summary
        else:
            print(summary)

    def missing_items(self, return_type='print'):
        """
        Identify elements that may be missing child elements based on the contents of other sibling nodes.

        Parameters
        ----------
        return_type : {'print', 'string', 'dict'}, default 'print'
            If 'print', then a string that enumerates the missing items will be
            printed. If 'string', then that same string will be returned and not
            printed. If 'dict', then a dictionary that maps element paths to lists
            of their potential missing children will be returned.
        """
        if return_type.lower() not in ['print', 'str', 'string', 'dict', 'dictionary', 'map']:
            raise SPyValueError(f"Illegal argument {return_type} for return_type. Acceptable values are 'print', "
                                f"'string', and 'dict'.")
        return_type = return_type.lower()

        if self.count(item_type='Asset') == self.size:
            missing_string = 'There are no non-asset items in your tree.'
            if return_type in ['dict', 'dictionary', 'map']:
                return dict()
            elif return_type == 'print':
                print(missing_string)
                return
            else:
                return missing_string

        repeated_grandchildren = dict()

        prev_row = None
        path_stack = []
        for _, row in self._dataframe.iterrows():
            if prev_row is None:
                pass
            elif row.Depth > prev_row.Depth:
                path_stack.append((prev_row, set()))
            else:
                path_stack = path_stack[:row.Depth - 1]
            if len(path_stack) > 1:
                grandparent, grandchildren_set = path_stack[-2]
                if row.Name in grandchildren_set:
                    repeated_grandchildren.setdefault(_path.get_full_path(grandparent),
                                                      set()).add(row.Name)
                else:
                    grandchildren_set.add(row.Name)
            prev_row = row

        missing_item_map = dict()
        path_stack = []
        for _, row in self._dataframe.iterrows():
            if prev_row is None:
                pass
            elif row.Depth > prev_row.Depth:
                if path_stack and _path.get_full_path(
                        path_stack[-1][0]) in repeated_grandchildren:
                    required_children = repeated_grandchildren[
                        _path.get_full_path(path_stack[-1][0])].copy()
                else:
                    required_children = set()
                path_stack.append((prev_row, required_children))
            else:
                for parent, required_children in path_stack[row.Depth - 1:]:
                    if len(required_children) != 0:
                        missing_item_map[_path.get_full_path(parent)] = sorted(required_children)
                path_stack = path_stack[:row.Depth - 1]
            if len(path_stack) != 0:
                _, required_children = path_stack[-1]
                required_children.discard(row.Name)
            prev_row = row
        for parent, required_children in path_stack:
            if len(required_children) != 0:
                missing_item_map[_path.get_full_path(parent)] = sorted(required_children)

        if return_type in ['dict', 'dictionary', 'map']:
            return missing_item_map

        if len(missing_item_map):
            missing_string = 'The following elements appear to be missing:'
            for parent_path, missing_children in missing_item_map.items():
                missing_string += f"\n{parent_path} is missing: {', '.join(missing_children)}"
        else:
            missing_string = 'No items are detected as missing.'

        if return_type == 'print':
            print(missing_string)
        else:
            return missing_string

    @property
    def name(self):
        return self._dataframe.loc[0, 'Name']

    @name.setter
    def name(self, value):
        _common.validate_argument_types([(value, 'name', str)])

        df = _utils.set_name(self._dataframe, value)
        _validate.validate_and_filter(self.session, df, Status(quiet=True), errors='raise',
                                      stage='final',
                                      error_message_header='Errors encountered after changing tree root name')

        self._dataframe = df

    def push(self, *, errors=None, quiet=None, status=None):
        """
        Imports the tree into Seeq Server.

        errors : {'raise', 'catalog'}, optional
            If 'raise', any errors encountered will cause an exception. If 'catalog',
            errors will be added to a 'Result' column in the status.df DataFrame. This
            input will be used only for the duration of this function; it will default
            to the setting on the Tree if not specified.

        quiet : bool, optional
            If True, suppresses progress output. This input will be used only for the
            duration of this function; it will default to the setting on the Tree if
            not specified. Note that when status is provided, the quiet setting of
            the Status object that is passed in takes precedent.

        status : spy.Status, optional
            If specified, the supplied Status object will be updated as the command
            progresses. It gets filled in with the same information you would see
            in Jupyter in the blue/green/red table below your code while the
            command is executed. The table itself is accessible as a DataFrame via
            the status.df property.
        """
        _common.validate_argument_types([
            (errors, 'errors', str),
            (quiet, 'quiet', bool),
            (status, 'status', Status)
        ])

        errors = self._get_or_default_errors(errors)
        quiet = self._get_or_default_quiet(quiet)
        status = Status.validate(status, quiet)

        df_to_push = _properties.format_formula_parameters(self._dataframe, status)

        push_results = _push.push(metadata=df_to_push, workbook=self._workbook, datasource=self._datasource,
                                  archive=True, errors=errors, quiet=quiet, status=status, session=self.session)

        if self._workbook_id == _common.EMPTY_GUID:
            self._find_workbook_id(quiet, status)

        successfully_pushed = push_results['Push Result'] == 'Success'
        self._dataframe.loc[successfully_pushed, 'ID'] = push_results.loc[successfully_pushed, 'ID']
        self._dataframe.loc[successfully_pushed, 'Type'] = push_results.loc[successfully_pushed, 'Type']

        return push_results

    def _ipython_display_(self):
        self.summarize()

    def __iter__(self):
        return self._dataframe.itertuples(index=False, name='Item')

    def _find_workbook_id(self, quiet, status):
        """
        Set the _workbook_id based on the workbook input. This will enable us to know whether we should set
        the `ID` or `Referenced ID` column when pulling an item.
        """
        if _common.is_guid(self._workbook):
            self._workbook_id = _common.sanitize_guid(self._workbook)
        elif self.session.client:
            search_query, _ = _push.create_analysis_search_query(self._workbook)
            search_df = spy.workbooks.search(search_query,
                                             quiet=quiet,
                                             status=status.create_inner('Find Workbook', quiet=quiet),
                                             session=self.session)
            self._workbook_id = search_df.iloc[0]['ID'] if len(search_df) > 0 else _common.EMPTY_GUID
        else:
            self._workbook_id = _common.EMPTY_GUID

    def _get_or_default_errors(self, errors_input):
        if isinstance(errors_input, str):
            _common.validate_errors_arg(errors_input)
            return errors_input
        return self.errors

    def _get_or_default_quiet(self, quiet_input):
        if isinstance(quiet_input, bool):
            return quiet_input
        return self.quiet
