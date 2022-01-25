import re
import unittest.mock

import numpy as np
import pandas as pd
import pytest

from seeq import spy
from seeq.spy import _common
from seeq.spy._status import Status
from seeq.spy.assets._trees import Tree
from seeq.spy.assets._trees import _constants, _csv, _match, _path, _properties, _utils, _validate
from seeq.spy.assets._trees.tests.test_tree_system import assert_tree_equals_expected


def assert_frame_equal(df1, df2):
    # noinspection PyProtectedMember
    return pd._testing.assert_frame_equal(df1.sort_index(axis=1),
                                          df2.sort_index(axis=1),
                                          check_dtype=False)


def _tree_from_nested_dict(d):
    if len(d) != 1:
        raise ValueError('Cannot have more than one root.')

    root_name, root_branches = [(k, v) for k, v in d.items()][0]
    tree = Tree(root_name)

    def _add_branches(parent_name, branches_dict):
        for branch_name, sub_branches in branches_dict.items():
            tree.insert(branch_name, parent_name)
            _add_branches(branch_name, sub_branches)

    _add_branches(root_name, root_branches)
    return tree


def _build_dataframe_from_path_name_depth_triples(data):
    df = pd.DataFrame(columns=_constants.dataframe_columns)
    return df.append([{
        'Type': 'Asset',
        'Path': path,
        'Depth': depth,
        'Name': name,
    } for path, name, depth in data])


@pytest.mark.unit
def test_constructor_invalid():
    # Basic property validation
    with pytest.raises(TypeError, match="Argument 'data' should be type DataFrame or str, but is type int"):
        Tree(0)
    with pytest.raises(TypeError, match="'data' must be a name, name of a csv file, Seeq ID, or Metadata dataframe"):
        Tree(data='')
    with pytest.raises(TypeError, match="'data' must be a name, name of a csv file, Seeq ID, or Metadata dataframe"):
        Tree(None)
    with pytest.raises(ValueError, match="DataFrame with no rows"):
        Tree(pd.DataFrame(columns=['Name']))
    with pytest.raises(TypeError, match="Argument 'description' should be type str"):
        Tree('name', description=0)
    with pytest.raises(TypeError, match="Argument 'workbook' should be type str"):
        Tree('name', workbook=0)
    with pytest.raises(TypeError, match="should be type DataFrame or str, but is type Tree"):
        Tree(Tree('Tree Inception'))

    df = pd.DataFrame([{'Name': 'root1', 'Type': 'Asset'}, {'Name': 'root2', 'Type': 'Asset'}])
    with pytest.raises(RuntimeError, match="A tree can only have one root"):
        Tree(df)

    with pytest.raises(RuntimeError, match="Not logged in"):
        Tree('8DEECF16-A500-4231-939D-6C24DD123A30')


@pytest.mark.unit
def test_constructor_name():
    # Valid constructor for a new root asset with all other properties default
    name = 'test name'
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'test name', 1)
    ])
    test_tree = Tree(name)
    assert test_tree._dataframe.columns.equals(expected.columns)
    assert test_tree._dataframe.iloc[0].equals(expected.iloc[0])
    assert test_tree._workbook == spy._common.DEFAULT_WORKBOOK_PATH

    # Valid constructor for a new root asset with all other properties assigned to non-defaults
    description = 'test description'
    workbook = 'test workbook'
    expected['Description'] = [description]
    test_tree = Tree(name, description=description, workbook=workbook)
    assert_frame_equal(test_tree._dataframe, expected)
    assert test_tree._workbook == workbook


@pytest.mark.unit
def test_insert_by_name():
    tree_dict = {
        'Root Asset': {
            'L Asset': {
                'LL Asset': {},
                'LR Asset': {}
            },
            'R Asset': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'L Asset', 2),
        ('Root Asset >> L Asset', 'LL Asset', 3),
        ('Root Asset >> L Asset', 'LR Asset', 3),
        ('Root Asset', 'R Asset', 2),
    ])
    assert_frame_equal(test_tree._dataframe, expected)


@pytest.mark.unit
def test_insert_by_name_list():
    tree_dict = {
        'Root Asset': {
            'Location A': {},
            'Location B': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert([f'Equipment {n}' for n in range(1, 4)], parent='Location A')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Location A', 2),
        ('Root Asset >> Location A', 'Equipment 1', 3),
        ('Root Asset >> Location A', 'Equipment 2', 3),
        ('Root Asset >> Location A', 'Equipment 3', 3),
        ('Root Asset', 'Location B', 2),
    ])
    assert_frame_equal(test_tree._dataframe, expected)


@pytest.mark.unit
def test_insert_at_depth():
    tree_dict = {
        'Root Asset': {
            'Location A': {},
            'Location B': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert([f'Equipment {n}' for n in range(1, 4)], parent=2)
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Location A', 2),
        ('Root Asset >> Location A', 'Equipment 1', 3),
        ('Root Asset >> Location A', 'Equipment 2', 3),
        ('Root Asset >> Location A', 'Equipment 3', 3),
        ('Root Asset', 'Location B', 2),
        ('Root Asset >> Location B', 'Equipment 1', 3),
        ('Root Asset >> Location B', 'Equipment 2', 3),
        ('Root Asset >> Location B', 'Equipment 3', 3),
    ])
    assert_frame_equal(test_tree._dataframe, expected)


@pytest.mark.unit
def test_insert_at_path():
    tree_dict = {
        'Root Asset': {
            'Factory': {
                'Location A': {},
                'Location B': {}
            }
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    # Test partial path match with regex
    test_tree.insert('Equipment 1', parent='Factory >> Location [A-Z]')
    # Test full path match with case insensitivity
    test_tree.insert('Equipment 2', parent='rOoT aSsEt >> FaCtOrY >> lOcAtIoN b')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Factory', 2),
        ('Root Asset >> Factory', 'Location A', 3),
        ('Root Asset >> Factory >> Location A', 'Equipment 1', 4),
        ('Root Asset >> Factory', 'Location B', 3),
        ('Root Asset >> Factory >> Location B', 'Equipment 1', 4),
        ('Root Asset >> Factory >> Location B', 'Equipment 2', 4),
    ])
    assert_frame_equal(test_tree._dataframe, expected)


@pytest.mark.unit
def test_insert_at_root():
    tree_dict = {
        'Root Asset': {
            'Location A': {},
            'Location B': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert('Location C')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Location A', 2),
        ('Root Asset', 'Location B', 2),
        ('Root Asset', 'Location C', 2),
    ])
    assert_frame_equal(test_tree._dataframe, expected)


@pytest.mark.unit
def test_insert_at_regex():
    tree_dict = {
        'Root Asset': {
            'Factory': {
                'Location Z': {}
            },
            'Area 51': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert('Equipment 1', parent='Area [1-9][0-9]*|Location [A-Z]+')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Area 51', 2),
        ('Root Asset >> Area 51', 'Equipment 1', 3),
        ('Root Asset', 'Factory', 2),
        ('Root Asset >> Factory', 'Location Z', 3),
        ('Root Asset >> Factory >> Location Z', 'Equipment 1', 4)
    ])
    assert_frame_equal(test_tree._dataframe, expected)


@pytest.mark.unit
def test_insert_at_glob():
    tree_dict = {
        'Root Asset': {
            'Location A': {},
            'Location 1': {}
        }
    }
    test_tree = _tree_from_nested_dict(tree_dict)
    test_tree.insert('Equipment 1', parent='Location ?')
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root Asset', 1),
        ('Root Asset', 'Location 1', 2),
        ('Root Asset >> Location 1', 'Equipment 1', 3),
        ('Root Asset', 'Location A', 2),
        ('Root Asset >> Location A', 'Equipment 1', 3)
    ])
    assert_frame_equal(test_tree._dataframe, expected)


@pytest.mark.unit
def test_insert_preexisting_node():
    tree_dict = {
        'Root': {
            'Location A': {}
        }
    }
    tree = _tree_from_nested_dict(tree_dict)
    tree.insert('lOcAtIoN a')
    expected = _tree_from_nested_dict(tree_dict)
    assert_frame_equal(tree._dataframe, expected._dataframe)


@pytest.mark.unit
def test_insert_same_node_twice():
    tree_dict = {
        'Root': {}
    }
    tree = _tree_from_nested_dict(tree_dict)
    expected_dict = {
        'Root': {
            'Location A': {}
        }
    }
    expected = _tree_from_nested_dict(expected_dict)
    tree.insert(['Location A', 'Location A'])
    assert_frame_equal(tree._dataframe, expected._dataframe)


@pytest.mark.unit
def test_insert_no_parent_match():
    tree = Tree('Root')

    status = Status()
    tree.insert(children=['Child 1', 'Child 2'], parent=3, status=status)
    assert 'No matching parents found. Nothing was inserted.' in status.warnings

    status = Status()
    tree.insert(children=['Child 1', 'Child 2'], parent='asdf', status=status)
    assert 'No matching parents found. Nothing was inserted.' in status.warnings


@pytest.mark.unit
def test_constructor_dataframe_implied_and_leading_assets():
    # The constructor will imply assets and remove redundant leading assets.
    # Even though 'Root' and 'Location B' are not explicitly stated, they must exist for this to be a valid tree.
    insertions = _build_dataframe_from_path_name_depth_triples([
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Location A', 7),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root >> Location A', 'Equipment 1', 8),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root >> Location B', 'Equipment 2', 8),
    ])
    tree = Tree(insertions)
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root', 'Location B', 2),
        ('Root >> Location B', 'Equipment 2', 3),
    ])
    assert_frame_equal(tree._dataframe, expected)

    # And try with Path+Asset columns
    insertions = _build_dataframe_from_path_name_depth_triples([
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Equipment 1', 8),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Equipment 2', 8),
    ])
    insertions['Asset'] = ['Location A', 'Location B']
    tree = Tree(insertions)
    assert_frame_equal(tree._dataframe, expected)


@pytest.mark.unit
def test_insert_dataframe_implied_and_leading_assets():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root', 'Location B', 2),
        ('Root >> Location B', 'Equipment 2', 3),
    ])
    insertions = _build_dataframe_from_path_name_depth_triples([
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root >> Location A', 'Equipment 1', 8),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root >> Location B', 'Equipment 2', 8),
    ])
    tree = Tree('Root')
    status = Status()
    tree.insert(insertions, status=status)
    assert_frame_equal(tree._dataframe, expected)
    assert status.df.squeeze()['Total Items Inserted'] == 4

    # And try with Path+Asset columns
    insertions = _build_dataframe_from_path_name_depth_triples([
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Equipment 1', 8),
        ('Redundant >> Assets >> Will >> Be >> Removed >> Root', 'Equipment 2', 8),
    ])
    insertions['Asset'] = ['Location A', 'Location B']
    tree = Tree('Root')
    status = Status()
    tree.insert(insertions, status=status)
    assert_frame_equal(tree._dataframe, expected)
    assert status.df.squeeze()['Total Items Inserted'] == 4


@pytest.mark.unit
def test_insert_dataframe_name_only():
    expected1 = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root', 'Location B', 2),
    ])
    insertions1 = pd.DataFrame([{'Name': 'Location A'}, {'Name': 'Location B'}])
    tree = Tree('Root')
    status = Status()
    tree.insert(insertions1, status=status)
    assert_frame_equal(tree._dataframe, expected1)
    assert status.df.squeeze()['Total Items Inserted'] == 2
    assert status.df.squeeze()['Assets Inserted'] == 2

    expected2 = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root >> Location A', 'Equipment 2', 3),
        ('Root', 'Location B', 2),
        ('Root >> Location B', 'Equipment 1', 3),
        ('Root >> Location B', 'Equipment 2', 3),
    ])
    insertions2 = pd.DataFrame([{'Name': 'Equipment 1'}, {'Name': 'Equipment 2'}])
    status = Status()
    tree.insert(insertions2, parent='location *', status=status)
    assert_frame_equal(tree._dataframe, expected2)
    assert status.df.squeeze()['Total Items Inserted'] == 4
    assert status.df.squeeze()['Assets Inserted'] == 4


@pytest.mark.unit
def test_insert_dataframe_missing_name():
    insertions = pd.DataFrame([{'Formula': 'days()'}])
    tree = Tree('Root')
    with pytest.raises(RuntimeError, match="'Name' or 'Friendly Name' is required"):
        tree.insert(insertions)


@pytest.mark.unit
def test_insert_non_string_children_with_formula_or_formula_params_dataframe_case():
    tree = Tree('Children Tree')
    children_df = pd.DataFrame([{'Name': 'Child 1'}, {'Name': 'Child 2'}])
    tree.insert(children_df, formula='sinusoid()')
    expected = list()
    expected.append({
        'Name': 'Children Tree',
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Child 1',
        'Path': 'Children Tree',
        'Formula': 'sinusoid()'
    })
    expected.append({
        'Name': 'Child 2',
        'Path': 'Children Tree',
        'Formula': 'sinusoid()'
    })
    assert_tree_equals_expected(tree, expected)

    # second case (testing with formula parameters)
    children_df_2 = pd.DataFrame([{'Name': 'Child 3'}, {'Name': 'Child 4'}])
    tree.insert(children_df_2, formula='$x', formula_parameters='$x=Child 1', parent='Children Tree')
    expected.append({
        'Name': 'Child 3',
        'Path': 'Children Tree',
        'Formula': '$x',
        'Formula Parameters': {'$x': 'Child 1'}
    })
    expected.append({
        'Name': 'Child 4',
        'Path': 'Children Tree',
        'Formula': '$x',
        'Formula Parameters': {'$x': 'Child 1'}
    })
    assert_tree_equals_expected(tree, expected)


@pytest.mark.unit
def test_insert_tree_and_formula_case_fail():
    tree = Tree('Main Tree')
    child_tree = Tree('Child Tree')
    children_df = pd.DataFrame([{'Name': 'Child 1'}, {'Name': 'Child 2'}])
    child_tree.insert(children_df)
    with pytest.raises(Exception, match="Children DataFrame cannot contain a 'Formula' or 'Formula Parameters'"):
        tree.insert(child_tree, formula='sinusoid()')
    with pytest.raises(Exception, match="Children DataFrame cannot contain a 'Formula' or 'Formula Parameters'"):
        tree.insert(child_tree, formula_parameters='$x=sinusoid()', formula='$x')


@pytest.mark.unit
def test_dataframe_with_assets_insert_with_formula_fail_case():
    tree = Tree('dataframe_case')
    children_df = pd.DataFrame([{'Name': 'Asset 1', 'Type': 'Asset'}])
    with pytest.raises(Exception, match="Assets cannot have formulas or formula parameters."):
        tree.insert(children_df, formula='sinusoid')


@pytest.mark.unit
def test_children_used_as_friendly_name_string_case():
    tree = Tree('children_as_name')
    tree.insert('My Calculation', formula='some_formula()')
    expected = list()
    expected.append({
        'Name': 'children_as_name',
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'My Calculation',
        'Path': 'children_as_name',
        'Type': pd.NA,
        'Formula': 'some_formula()'
    })
    assert_tree_equals_expected(tree, expected)

    # second case (testing with formula parameters)
    param_id = _common.new_placeholder_guid()
    tree.insert('My Second Calculation', formula='$x', formula_parameters=f'$x={param_id}',
                parent='children_as_name')
    expected.append({
        'Name': 'My Second Calculation',
        'Path': 'children_as_name',
        'Type': pd.NA,
        'Formula': '$x',
        'Formula Parameters': {'$x': param_id}
    })
    assert_tree_equals_expected(tree, expected)


@pytest.mark.unit
def test_children_used_as_friendly_name_list_case():
    tree = Tree('children_list_as_name')
    children_list = ['My Calculation', 'My Second Calculation']
    tree.insert(children_list, formula='some_formula()')
    expected = list()
    expected.append({
        'Name': 'children_list_as_name',
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'My Calculation',
        'Path': 'children_list_as_name',
        'Type': pd.NA,
        'Formula': 'some_formula()'
    })
    expected.append({
        'Name': 'My Second Calculation',
        'Path': 'children_list_as_name',
        'Type': pd.NA,
        'Formula': 'some_formula()'
    })
    assert_tree_equals_expected(tree, expected)

    # second case (testing with formula parameters)
    param_id = _common.new_placeholder_guid()
    children_list_2 = ['My Third Calculation', 'My Fourth Calculation']
    tree.insert(children_list_2, formula='$x', formula_parameters=f'$x={param_id}',
                parent='children_list_as_name')
    expected.append({
        'Name': 'My Third Calculation',
        'Path': 'children_list_as_name',
        'Type': pd.NA,
        'Formula': '$x',
        'Formula Parameters': {'$x': param_id}
    })
    expected.append({
        'Name': 'My Fourth Calculation',
        'Path': 'children_list_as_name',
        'Type': pd.NA,
        'Formula': '$x',
        'Formula Parameters': {'$x': param_id}
    })
    assert_tree_equals_expected(tree, expected)


@pytest.mark.unit
def test_insert_missing_input():
    tree = Tree('test_tree_system10')
    tree.insert('Asset')

    tree.insert(pd.DataFrame([{
        'Name': 'Insert Invalid Formula',
        'Formula': 'sinusoid()'
    }]), parent='Asset')

    with pytest.raises(Exception, match='Must have a Formula if Formula Parameters are defined.'):
        tree.insert(pd.DataFrame([{
            'Name': 'test',
            'Formula Parameters': 'x=Insert Invalid Formula'
        }]), parent='Asset')

    with pytest.raises(Exception, match='All Signals and Conditions require either a formula or an ID'):
        tree.insert(pd.DataFrame([{
            'Name': 'Insert Empty Formula',
            'Type': 'Signal',
            'Formula': ''
        }]), parent='Asset')

    with pytest.raises(Exception, match="The property 'Type' is required for all items without formulas."):
        tree.insert(pd.DataFrame([{
            'Name': 'Insert Invalid Formula No Type',
            'Formula': ''
        }]), parent='Asset')

    with pytest.raises(Exception, match="The property 'Name' or 'Friendly Name' is required"):
        tree.insert(pd.DataFrame([{
            'Formula': 'sinusoid()'
        }]), parent='Asset')


@pytest.mark.unit
def test_formula_params_to_dict_strip():
    tree = Tree('Cases with Spaces')
    param_id = _common.new_placeholder_guid()
    tree.insert(None, formula='$x', formula_parameters=f'  x    =    {param_id}  ', friendly_name='Spacey')
    expected = list()
    expected.append({
        'Name': 'Cases with Spaces',
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Spacey',
        'Path': 'Cases with Spaces',
        'Type': pd.NA,
        'Formula': '$x',
        'Formula Parameters': {'x': param_id}
    })


@pytest.mark.unit
def test_formula_params_to_dict():
    pandas_na_input = _properties.formula_parameters_to_dict(pd.NA)
    assert pd.isnull(pandas_na_input)

    none_input = _properties.formula_parameters_to_dict(None)
    assert pd.isnull(none_input)

    empty_string_input = _properties.formula_parameters_to_dict('')
    assert empty_string_input == {}

    empty_list_input = _properties.formula_parameters_to_dict([])
    assert empty_list_input == {}

    empty_dict_input = _properties.formula_parameters_to_dict({})
    assert empty_dict_input == {}

    string_input = _properties.formula_parameters_to_dict('$x=sinusoid()')
    assert string_input == {'$x': 'sinusoid()'}

    series_data = ['$x=sinusoid()', '$y=cosinusoid()']
    series_index = [1, 2]
    series_input = _properties.formula_parameters_to_dict(pd.Series(data=series_data, index=series_index))
    assert series_input == {'$x': 'sinusoid()', '$y': 'cosinusoid()'}

    list_input = _properties.formula_parameters_to_dict(['$x = sinusoid()', '$y=cosinusoid()'])
    assert list_input == {'$x': 'sinusoid()', '$y': 'cosinusoid()'}


@pytest.mark.unit
def test_formula_insert():
    tree = Tree('Test Formula Insert')

    tree.insert(children=None, formula='$x', formula_parameters='x=A1C58783-5951-413F-A584-D73CED2C0191',
                friendly_name='Test Formula Parameters')
    tree.insert(children=None, friendly_name='Test No Formula Parameters', formula='sinusoid()')
    expected = list()
    expected.append({
        'Name': 'Test Formula Insert',
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Test Formula Parameters',
        'Path': 'Test Formula Insert',
        'Type': pd.NA,
        'Formula Parameters': {'x': 'A1C58783-5951-413F-A584-D73CED2C0191'},
        'Formula': '$x'
    })
    expected.append({
        'Name': 'Test No Formula Parameters',
        'Path': 'Test Formula Insert',
        'Type': pd.NA,
        'Formula': 'sinusoid()'
    })
    assert_tree_equals_expected(tree, expected)

    with pytest.raises(Exception, match='Friendly Name must be specified if no children argument is given.'):
        tree.insert(children=None, formula='$x')


@pytest.mark.unit
def test_formula_parameters_ignored():
    tree = Tree('Ignore Formula Parameters')
    dataframe = pd.DataFrame([{'Name': 'Asset 1'}, {'Name': 'Asset 2'}])
    tree.insert(dataframe, formula_parameters='$x=ignore()')
    expected = list()
    expected.append({
        'Name': 'Ignore Formula Parameters',
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Asset 1',
        'Path': 'Ignore Formula Parameters',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Asset 2',
        'Path': 'Ignore Formula Parameters',
        'Type': 'Asset'
    })
    assert_tree_equals_expected(tree, expected)


@pytest.mark.unit
def test_formula_parameters_to_dict():
    formula_parameters_empty = _properties.formula_parameters_to_dict(None)
    assert pd.isnull(formula_parameters_empty)

    formula_string = 'x=42'
    formula_parameters_string = _properties.formula_parameters_to_dict(formula_string)
    assert isinstance(formula_parameters_string, dict)
    expected_dict_string = {'x': '42'}
    shared_items = {k: formula_parameters_string[k] for k in formula_parameters_string if
                    k in expected_dict_string and formula_parameters_string[k]
                    == expected_dict_string[k]}
    assert len(shared_items) == 1

    formula_list = ['x=1', 'y=2', 'z=3', 'a=4']
    formula_parameters_list = _properties.formula_parameters_to_dict(formula_list)
    assert isinstance(formula_parameters_list, dict)
    expected_dict_list = {'x': '1', 'y': '2', 'z': '3', 'a': '4'}
    shared_items = {k: formula_parameters_list[k] for k in formula_parameters_list if
                    k in expected_dict_list and formula_parameters_list[k]
                    == expected_dict_list[k]}
    assert len(shared_items) == 4

    invalid_formula_syntax_empty = []
    formula_parameters_empty = _properties.formula_parameters_to_dict(invalid_formula_syntax_empty)
    assert isinstance(formula_parameters_empty, dict)
    assert len(formula_parameters_empty) == 0

    invalid_formula_syntax_no_equals = ['x=1', 'y2', 'z=3', 'a=4']
    with pytest.raises(Exception, match='needs to be in the format \'paramName=inputItem\''):
        _properties.formula_parameters_to_dict(invalid_formula_syntax_no_equals)

    invalid_formula_syntax_double_equals = ['x=1', 'y==2', 'z=3', 'a=4']
    with pytest.raises(Exception, match='needs to be in the format \'paramName=inputItem\''):
        _properties.formula_parameters_to_dict(invalid_formula_syntax_double_equals)


@pytest.mark.unit
def test_insert_dataframe_metric():
    insertions = pd.DataFrame([{'Name': 'Location A', 'Type': 'Metric'}])
    tree = Tree('Root')
    status = Status()
    tree.insert(insertions, errors='catalog', status=status)
    assert status.df.squeeze()['Total Items Inserted'] == 0
    assert status.df.squeeze()['Errors Encountered'] == 1


@pytest.mark.unit
def test_insert_dataframe_weird_index():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Optimizer', 2),
        ('Root', 'Temperature', 2),
    ])
    insertions = pd.DataFrame([{'Name': 'Optimizer'}, {'Name': 'Temperature'}],
                              index=['some index', 'does not actually matter'])
    tree = Tree('Root')
    status = Status()
    tree.insert(insertions, status=status)
    assert_frame_equal(tree._dataframe, expected)
    assert status.df.squeeze()['Total Items Inserted'] == 2


@pytest.mark.unit
def test_insert_dataframe_mixed_scope():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Optimizer', 2),
        ('Root', 'Temperature', 2),
    ])
    insertions = pd.DataFrame([{'Name': 'Optimizer', 'Scoped To': np.nan},
                               {'Name': 'Temperature', 'Scoped To': '48C3002F-BBEA-4143-8765-D7DADD4E0CA2'}])
    tree = Tree('Root')
    status = Status()
    tree.insert(insertions, status=status)
    assert_frame_equal(tree._dataframe, expected)
    assert status.df.squeeze()['Total Items Inserted'] == 2


@pytest.mark.unit
def test_insert_dataframe_with_mixed_path_existence():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
    ])
    # Inserting a NaN path implies that 'Location A' is the sub-root
    insertions = pd.DataFrame([{'Name': 'Location A', 'Path': np.nan},
                               {'Name': 'Equipment 1', 'Path': 'Location A'}])
    tree = Tree('Root')
    status = Status()
    tree.insert(insertions, status=status)
    assert_frame_equal(tree._dataframe, expected)
    assert status.df.squeeze()['Total Items Inserted'] == 2


@pytest.mark.unit
def test_validate_empty_df():
    df = pd.DataFrame(columns=['Any', 'Columns', 'You', 'Want'])
    error_summaries, error_series = _validate.validate(spy.session, df)
    assert len(error_summaries) == 1
    assert 'Tree must be non-empty' in error_summaries[0]
    assert len(error_series) == 0


@pytest.mark.unit
def test_validate_bad_depth():
    df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root >> Location A', 'Equipment 2', 1),
    ])
    error_summaries, error_series = _validate.validate(spy.session, df)
    assert len(error_summaries) == 1
    error_msg = 'Item\'s depth does not match its path'
    assert error_msg in error_summaries[0]
    assert error_msg in error_series[3]

    df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 3)
    ])
    error_summaries, error_series = _validate.validate(spy.session, df)
    assert len(error_summaries) == 1
    error_msg = 'Item\'s depth does not match its path'
    assert error_msg in error_summaries[0]
    assert error_msg in error_series[1]


@pytest.mark.unit
def test_validate_root():
    df = _build_dataframe_from_path_name_depth_triples([
        ('Super-root', 'Root', 2),
        ('Super-root >> Root', 'Item', 3)
    ])
    error_summaries, error_series = _validate.validate(spy.session, df)
    assert len(error_summaries) == 1
    error_msg = 'The root of the tree cannot be assigned a path.'
    assert error_msg in error_summaries[0]
    assert error_msg in error_series[0]

    df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Item', 2),
        ('', 'Another Root', 1)
    ])
    error_summaries, error_series = _validate.validate(spy.session, df)
    assert len(error_summaries) == 1
    error_msg = 'A tree can only have one root'
    assert error_msg in error_summaries[0]
    assert error_msg in error_series[2]


@pytest.mark.unit
def test_validate_bad_path():
    df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location A', 2),
        ('Root >> Locat--TYPO--ion A', 'Equipment 1', 3),
        ('Root >> Location A', 'Equipment 2', 3),
    ])
    error_summaries, error_series = _validate.validate(spy.session, df)
    assert len(error_summaries) == 1
    error_msg = 'Item\'s position in tree does not match its path.'
    assert error_msg in error_summaries[0]
    assert error_msg in error_series[2]


@pytest.mark.unit
def test_validate_path_sort():
    df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Location B', 2),
        ('Root >> Location B', 'Equipment 1', 3),
        ('Root', 'Location A', 2),
    ])
    error_summaries, error_series = _validate.validate(spy.session, df)
    assert len(error_summaries) == 1
    error_msg = 'Item is not stored in proper position sorted by path.'
    assert error_msg in error_summaries[0]
    assert error_msg in error_series[3]


@pytest.mark.unit
def test_validate_all_assets_exist():
    df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root >> Location A', 'Equipment 1', 3),
        ('Root', 'Location B', 2),
    ])
    error_summaries, error_series = _validate.validate(spy.session, df)
    assert len(error_summaries) == 1
    error_msg = 'Item has an ancestor not stored in this tree.'
    assert error_msg in error_summaries[0]
    assert error_msg in error_series[1]


@pytest.mark.unit
def test_validate_invalid_parent():
    df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Bad Path', 'Location B', 2),
        ('Bad Path >> Location B', 'Area 1', 3),
        ('Bad Path', 'Location A', 2),
        ('Bad Path >> Location A', 'Area 2', 3),
    ])
    error_summaries, error_series = _validate.validate(spy.session, df)
    assert len(error_summaries) == 2
    assert (error_series.loc[[2, 4]] == 'Item\'s parent is invalid.').all()


@pytest.mark.unit
def test_validate_column_dtypes():
    df = pd.DataFrame([{
        'ID': 3.14159,
        'Referenced ID': -163,
        'Type': pd.Series([1, 2, 3]),
        'Path': set(),
        'Depth': pd.to_datetime('2020'),
        'Name': list(),
        'Description': False,
        'Formula': (),
        'Formula Parameters': 0.577215,
        'Cache Enabled': 'Yes'
    }])
    with unittest.mock.patch('seeq.spy.assets._trees._constants.MAX_ERRORS_DISPLAYED', new=999):
        error_summaries, error_series = _validate.validate(spy.session, df)
    for column in _constants.dataframe_columns:
        error_msg = f"The property '{column}' must have one of the following types"
        assert any([error_msg in x for x in error_summaries])
        assert error_msg in error_series[0]


@pytest.mark.unit
def test_validate_properties():
    df = pd.DataFrame([
        {},
        {'Name': 'My Condition', 'Type': 'Condition'},
        {'Name': 'My Formula Parameters', 'Formula Parameters': '$x=sinusoid()'},
        {'Name': 'My Metric', 'Type': 'Metric'},
        {'ID': '8DEECF16-A500-4231-939D-6C24DD123A30'},
        {'ID': 'bad-guid-format'},
        {'Referenced ID': 'bad-guid-format'},
        {'Name': 'Area A', 'Path': 'Example >> Cooling Tower 1 >> Cooling Tower 1'},
        {'Name': 'Asset', 'Type': 'Asset', 'Formula': 'sinusoid()'}
    ])
    _, error_series = _validate.validate(spy.session, df, stage='input')
    error_list = [
        "The property 'Name' or 'Friendly Name' is required for all nodes without ID.",
        "Stored Signals and Conditions are not yet supported. All Signals and Conditions require either a formula or "
        "an ID.",
        "Must have a Formula if Formula Parameters are defined.",
        "Threshold Metrics are not yet supported.",
        "Must log in via spy.login() before inserting an item via ID or Referenced ID.",
        "The property 'ID' must be a valid GUID. Given: 'bad-guid-format'",
        "The property 'Referenced ID' must be a valid GUID. Given: 'bad-guid-format'",
        "Paths with repeated names are not valid.",
        "Assets cannot have formulas or formula parameters."
    ]

    assert len(error_list) == len(_validate.property_validations(spy.session, dict(), 'input'))

    for i in range(len(error_list)):
        row_validation = _validate.property_validations(spy.session, df.iloc[i], 'input')
        assert row_validation[i][1] in error_series.loc[i]
        assert row_validation[i][1] in error_list[i]

    df = pd.DataFrame([
        {'Name': 'My Asset', 'Path': '', 'Depth': 1},
        {'Name': 'My Condition', 'Type': 'Condition', 'Path': '', 'Depth': 1},
        {'Name': 'My Formula Parameters', 'Type': 'Signal', 'Formula Parameters': '$x=sinusoid()', 'Path': '',
         'Depth': 1},
        {'Name': 'My Metric', 'Type': 'Metric', 'Path': '', 'Depth': 1},
        {'Path': '', 'Depth': 1, 'Type': 'Asset'},
        {'Name': 'My Asset', 'Depth': 1, 'Type': 'Asset'},
        {'Name': 'My Asset', 'Path': '', 'Type': 'Asset'},
        {'Name': 'Cooling Tower 1', 'Path': 'Example >> Cooling Tower 1', 'Type': 'Asset', 'Depth': 4},
        {'Name': 'Asset', 'Path': '', 'Type': 'Asset', 'Formula': 'sinusoid()', 'Depth': 1},
        {'Name': 'Calculation', 'Path': '', 'Formula': '$x', 'Formula Parameters': '$x=sinusoid()', 'Depth': 1}
    ])
    df['Depth'] = df['Depth'].astype('Int64')
    _, error_series = _validate.validate(spy.session, df, stage='final')
    final_error_list = [
        "The property 'Type' is required for all items without formulas.",
        "Stored Signals and Conditions are not yet supported. All Signals and Conditions require a formula.",
        "Must have a Formula if Formula Parameters are defined.",
        "Threshold Metrics are not yet supported.",
        "The property 'Name' is required.",
        "The property 'Path' is required.",
        "The property 'Depth' is required.",
        "Paths with repeated names are not valid.",
        "Assets cannot have formulas or formula parameters."
    ]

    assert len(final_error_list) == len(_validate.property_validations(spy.session, dict(), 'final'))

    for i in range(len(final_error_list)):
        row_validation = _validate.property_validations(spy.session, df.iloc[i], 'final')
        assert row_validation[i][1] in error_series.loc[i]
        assert row_validation[i][1] in final_error_list[i]


@pytest.mark.unit
def test_validate_calculations():
    param_guid = _common.new_placeholder_guid()
    df = Tree(pd.DataFrame([{
        'Name': 'Root'
    }, {
        'Name': 'Calculation',
        'Path': 'Root',
        'Formula': '$a + $b',
        'Formula Parameters': {'a': 'Sibling 1', 'b': 'Sibling 2 >> Sibling Child', 'c': param_guid}
    }, {
        'Name': 'Sibling 1',
        'Type': 'Signal',
        'Path': 'Root',
        'Formula': 'whatever'
    }, {
        'Name': 'Sibling 2',
        'Path': 'Root'
    }, {
        'Name': 'Sibling Child',
        'Path': 'Root >> Sibling 2',
        'Type': 'Signal',
        'Formula': 'whatever'
    }]))._dataframe

    # The creation of df tests that formula parameter validation works with good input
    assert df.loc[df.Name == 'Calculation', 'Formula Parameters'].iloc[0] == {'a': 'Sibling 1',
                                                                              'b': 'Sibling 2 >> Sibling Child',
                                                                              'c': param_guid}

    # We now modify df to test bad cases
    msg = 'Formula parameter is invalid, missing, or has been removed from tree: \"'

    df1 = df.copy()
    df1.loc[df1.Name == 'Sibling 1', 'Name'] = 'Modified Sibling 1'
    error_summaries, error_series = _validate.validate(spy.session, df1, stage='final')
    assert len(error_summaries) == 1
    assert (msg + 'Root >> Sibling 1') in error_summaries[0]
    assert (msg + 'Root >> Sibling 1') in error_series[1]

    df2 = df.copy()
    df2.loc[df2.Name == 'Sibling Child', 'Name'] = 'Modified Sibling Child'
    error_summaries, error_series = _validate.validate(spy.session, df2, stage='final')
    assert len(error_summaries) == 1
    assert (msg + 'Root >> Sibling 2 >> Sibling Child') in error_summaries[0]
    assert (msg + 'Root >> Sibling 2 >> Sibling Child') in error_series[1]

    df3 = df.copy()
    df3.loc[df3.Name == 'Sibling 1', 'Name'] = 'Modified Sibling 1'
    df3.loc[df3.Name == 'Sibling Child', 'Name'] = 'Modified Sibling Child'
    error_summaries, error_series = _validate.validate(spy.session, df3, stage='final')
    assert len(error_summaries) == 2
    assert (msg + 'Root >> Sibling 1') in error_summaries[0]
    assert (msg + 'Root >> Sibling 2 >> Sibling Child') in error_summaries[1]
    assert (msg + 'Root >> Sibling 1') in error_series[1]
    assert (msg + 'Root >> Sibling 2 >> Sibling Child') in error_series[1]


@pytest.mark.unit
def test_validate_remove_and_move():
    tree = Tree(pd.DataFrame([{
        'Name': 'Root'
    }, {
        'Name': 'asset',
        'Path': 'Root',
    }, {
        'Name': 'Dependency',
        'Path': 'Root',
        'Type': 'Signal',
        'Formula': 'whatever'
    }, {
        'Name': 'Calculation',
        'Path': 'Root',
        'Type': 'Signal',
        'Formula': '$x + $x',
        'Formula Parameters': {'x': 'Dependency'}
    }]))

    with pytest.raises(RuntimeError, match='Formula parameter is invalid, missing, or has been removed from tree: '
                                           '\"Root >> Dependency\"'):
        tree.remove('Dependency')

    with pytest.raises(RuntimeError, match='Formula parameter is invalid, missing, or has been removed from tree: '
                                           '\"Root >> Dependency\"'):
        tree.move('Dependency', 'asset')


@pytest.mark.unit
def test_insert_other_tree():
    tree_to_insert = Tree('Area A')
    tree_to_insert.insert(['Optimizer', 'Temperature'])

    # Insert a tree directly below the root. The old 'Area A' root will not be transferred over.
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Area A', 2),
        ('Real Root >> Area A', 'Optimizer', 3),
        ('Real Root >> Area A', 'Temperature', 3),
        ('Real Root', 'Tower', 2),
    ])
    tree = Tree('Real Root')
    tree.insert('Tower')
    tree.insert(tree_to_insert)
    assert_frame_equal(tree._dataframe, expected_df)
    # Do it again to show it up-serts the nodes
    tree.insert(tree_to_insert)
    assert_frame_equal(tree._dataframe, expected_df)

    # Insert a tree below multiple parents
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Tower 1', 2),
        ('Real Root >> Tower 1', 'Area A', 3),
        ('Real Root >> Tower 1 >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower 1 >> Area A', 'Temperature', 4),
        ('Real Root', 'Tower 2', 2),
        ('Real Root >> Tower 2', 'Area A', 3),
        ('Real Root >> Tower 2 >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower 2 >> Area A', 'Temperature', 4),
    ])
    tree = Tree('Real Root')
    tree.insert(['Tower 1', 'Tower 2'])
    tree.insert(tree_to_insert, parent='Tower*')
    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit
def test_trim_unneeded_paths_constructor():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Tower', 2),
        ('Real Root >> Tower', 'Area A', 3),
        ('Real Root >> Tower >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower >> Area A', 'Temperature', 4),
    ])
    # Test three leading nodes to be removed
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2', 'Real Root', 4),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root', 'Tower', 5),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower', 'Area A', 6),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower >> Area A', 'Optimizer', 7),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower >> Area A', 'Temperature', 7),
    ])
    tree = Tree(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test one leading node to be removed
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root', 'Real Root', 2),
        ('Dupe Root >> Real Root', 'Tower', 3),
        ('Dupe Root >> Real Root >> Tower', 'Area A', 4),
        ('Dupe Root >> Real Root >> Tower >> Area A', 'Temperature', 5),
        ('Dupe Root >> Real Root >> Tower >> Area A', 'Optimizer', 5),
    ])
    tree = Tree(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test no changes needed
    test_df = expected_df.copy()
    tree = Tree(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test with implied shared roots only
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Tower 1', 2),
        ('Real Root >> Tower 1', 'Area A', 3),
        ('Real Root >> Tower 1 >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower 1 >> Area A', 'Temperature', 4),
        ('Real Root', 'Tower 2', 2),
        ('Real Root >> Tower 2', 'Area A', 3),
        ('Real Root >> Tower 2 >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower 2 >> Area A', 'Temperature', 4),
    ])
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower 1 >> Area A', 'Temperature', 4),
        ('Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower 1 >> Area A', 'Optimizer', 4),
        ('Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower 2 >> Area A', 'Temperature', 4),
        ('Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower 2 >> Area A', 'Optimizer', 4),
    ])
    tree = Tree(test_df)
    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit
def test_trim_unneeded_paths_insert():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Tower', 2),
        ('Real Root >> Tower', 'Area A', 3),
        ('Real Root >> Tower >> Area A', 'Optimizer', 4),
        ('Real Root >> Tower >> Area A', 'Temperature', 4),
    ])
    # Test three leading nodes to be removed with the same root as parent
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2', 'Real Root', 4),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root', 'Tower', 5),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower', 'Area A', 6),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower >> Area A', 'Temperature', 7),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Real Root >> Tower >> Area A', 'Optimizer', 7),
    ])
    tree = Tree('Real Root')
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test one leading node to be removed
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root', 'Real Root', 2),
        ('Dupe Root >> Real Root', 'Tower', 3),
        ('Dupe Root >> Real Root >> Tower', 'Area A', 4),
        ('Dupe Root >> Real Root >> Tower >> Area A', 'Temperature', 5),
        ('Dupe Root >> Real Root >> Tower >> Area A', 'Optimizer', 5),
    ])
    tree = Tree('Real Root')
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test no changes needed
    tree = Tree('Real Root')
    tree.insert(expected_df.copy())
    assert_frame_equal(tree._dataframe, expected_df)

    # Test three leading nodes to be removed with a different root as parent
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Sub Root', 2),
        ('Real Root >> Sub Root', 'Tower', 3),
        ('Real Root >> Sub Root >> Tower', 'Area A', 4),
        ('Real Root >> Sub Root >> Tower >> Area A', 'Optimizer', 5),
        ('Real Root >> Sub Root >> Tower >> Area A', 'Temperature', 5),
    ])
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2', 'Sub Root', 4),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Sub Root', 'Tower', 5),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Sub Root >> Tower', 'Area A', 6),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Sub Root >> Tower >> Area A', 'Temperature', 7),
        ('Dupe Root >> Dupe Path 1 >> Dupe Path 2 >> Sub Root >> Tower >> Area A', 'Optimizer', 7),
    ])
    tree = Tree('Real Root')
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)

    # Test with implied shared roots only
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Real Root', 1),
        ('Real Root', 'Sub Root', 2),
        ('Real Root >> Sub Root', 'Tower 1', 3),
        ('Real Root >> Sub Root >> Tower 1', 'Area A', 4),
        ('Real Root >> Sub Root >> Tower 1 >> Area A', 'Optimizer', 5),
        ('Real Root >> Sub Root >> Tower 1 >> Area A', 'Temperature', 5),
        ('Real Root >> Sub Root', 'Tower 2', 3),
        ('Real Root >> Sub Root >> Tower 2', 'Area A', 4),
        ('Real Root >> Sub Root >> Tower 2 >> Area A', 'Optimizer', 5),
        ('Real Root >> Sub Root >> Tower 2 >> Area A', 'Temperature', 5),
    ])
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Dupe Path >> Sub Root >> Tower 1 >> Area A', 'Temperature', 5),
        ('Dupe Path >> Sub Root >> Tower 1 >> Area A', 'Optimizer', 5),
        ('Dupe Path >> Sub Root >> Tower 2 >> Area A', 'Temperature', 5),
        ('Dupe Path >> Sub Root >> Tower 2 >> Area A', 'Optimizer', 5),
    ])
    tree = Tree('Real Root')
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)
    # Inserting that same thing again should be idempotent.
    tree.insert(test_df)
    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit
def test_reify_missing_assets():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Tower', 2),
        ('Root >> Tower', 'Region 1', 3),
        ('Root >> Tower >> Region 1', 'Area A', 4),
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1', 'Area B', 4),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower', 'Region 2', 3),
        ('Root >> Tower >> Region 2', 'Area C', 4),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    # Test everything missing except the leaf nodes
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    result_df = _path.reify_missing_assets(test_df)
    _path.sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)

    # Test everything missing between the root and the leaves
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    result_df = _path.reify_missing_assets(test_df)
    _path.sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)

    # Test missing the root-most two levels
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Root >> Tower', 'Region 1', 3),
        ('Root >> Tower >> Region 1', 'Area A', 4),
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1', 'Area B', 4),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower', 'Region 2', 3),
        ('Root >> Tower >> Region 2', 'Area C', 4),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    result_df = _path.reify_missing_assets(test_df)
    _path.sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)

    # Test no changes needed
    test_df = expected_df.copy()
    result_df = _path.reify_missing_assets(test_df)
    _path.sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)

    # Test where the first two levels should not be reified.
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('Root >> Tower', 'Region 1', 3),
        ('Root >> Tower >> Region 1', 'Area A', 4),
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1', 'Area B', 4),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower', 'Region 2', 3),
        ('Root >> Tower >> Region 2', 'Area C', 4),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    test_df = _build_dataframe_from_path_name_depth_triples([
        ('Root >> Tower >> Region 1 >> Area A', 'Optimizer', 5),
        ('Root >> Tower >> Region 1 >> Area A', 'Temperature', 5),
        ('Root >> Tower >> Region 1 >> Area B', 'Optimizer', 5),
        ('Root >> Tower >> Region 2 >> Area C', 'Temperature', 5),
    ])
    result_df = _path.reify_missing_assets(test_df, 'Root >> Tower')
    _path.sort_by_node_path(result_df)
    assert_frame_equal(result_df, expected_df)


@pytest.mark.unit
def test_upsert():
    df1 = pd.DataFrame([{
        'Path': 'Root',
        'Name': 'Area A',
        'Property': 'Anything',
        'Numerical': 123
    }, {
        'Path': 'Root >> Area A',
        'Name': 'Temperature',
        'Property': 'Old Value',
        'Numerical': 1,
        'Extra Old Column': 'Anything'
    }])
    df2 = pd.DataFrame([{
        'Path': 'Root >> Area A',
        'Name': 'Optimizer',
        'Property': 'Anything',
        'Numerical': 2,
        'Extra New Column': 'Something Unexpected'
    }, {
        'Path': 'root >> area A',
        'Name': 'temperature',
        'Property': 'New Value',
        'Numerical': np.nan,
        'Extra New Column': 'Something Unexpected'
    }])

    expected_df = pd.DataFrame([{
        'Path': 'Root',
        'Name': 'Area A',
        'Property': 'Anything',
        'Numerical': 123
    }, {
        'Path': 'Root >> Area A',
        'Name': 'Temperature',
        'Property': 'New Value',
        'Numerical': 1,
        'Extra Old Column': 'Anything'
    }, {
        'Path': 'Root >> Area A',
        'Name': 'Optimizer',
        'Property': 'Anything',
        'Numerical': 2
    }])

    upsert_df = _utils.upsert(df1, df2)
    assert_frame_equal(upsert_df, expected_df)
    assert upsert_df['Numerical'].dtype in [np.int32, np.int64]

    expected_df.loc[1, 'Property'] = 'Old Value'
    upsert_df = _utils.upsert(df1, df2, prefer_right=False)
    assert_frame_equal(upsert_df, expected_df)


@pytest.mark.unit
def test_insert_calculation_regex_asset_and_calculation_match():
    workbook = 'insert_several_similar_assets'
    tree = Tree('test_tree_system8', workbook=workbook)
    example_calc_id = _common.new_placeholder_guid()

    tree.insert('Area_A')
    tree.insert('Area_B')
    tree.insert('Area_C')

    tree.insert(pd.DataFrame([{
        'Name': 'Open Door B Please',
        'Formula Parameters': [f'x={example_calc_id}'],
        'Formula': '$x'
    }]), parent='Area_B')

    tree.insert(parent='Area_C', friendly_name='Open Door C Please', formula='$x',
                formula_parameters=[f'x={example_calc_id}'])

    with pytest.raises(RuntimeError, match='matches multiple items in tree'):
        tree.insert(pd.DataFrame([{
            'Name': 'Unspecified Door',
            'Formula Parameters': 'x=Area_* >> open*',
            'Formula': '$x'
        }]), parent='test_tree_system8')


@pytest.mark.unit
def test_asset_with_formula_fails():
    workbook = 'insert_asset_with_formula_and_or_formula_parameters'
    tree = Tree('test_tree_system9', workbook=workbook)

    with pytest.raises(Exception, match="Assets cannot have formulas or formula parameters"):
        tree.insert(pd.DataFrame([{
            'Name': 'Asset with formula',
            'Formula': 'sinusoid()',
            'Type': 'Asset'
        }]), parent='test_tree_system9')

    with pytest.raises(Exception, match="Assets cannot have formulas or formula parameters"):
        tree.insert(pd.DataFrame([{
            'Name': 'Asset with formula',
            'Formula Parameters': '$x=sinusoid()',
            'Type': 'Asset'
        }]), parent='test_tree_system9')

    with pytest.raises(Exception, match="Assets cannot have formulas or formula parameters"):
        tree.insert(pd.DataFrame([{
            'Name': 'Asset with formula',
            'Formula Parameters': '$x=sinusoid()',
            'Formula': '$x',
            'Type': 'Asset'
        }]), parent='test_tree_system9')


@pytest.mark.unit
def test_formula_parameter_pointing_to_asset_fail():
    spy.options.allow_version_mismatch = True
    workbook = 'asset_as_param'
    tree = Tree('test_tree_system11', workbook=workbook)
    tree.insert('Asset1')
    with pytest.raises(RuntimeError, match='Formula parameters must be conditions, scalars, or signals.'):
        tree.insert(pd.DataFrame([{
            'Name': "Fail Due To Asset As Param",
            'Formula Parameters': '$x = Asset1',
            'Formula': '$x'
        }]), parent='test_tree_system11')


@pytest.mark.unit
def test_move():
    tree = Tree('Root')
    tree.insert(['Cooling Tower 1', 'Cooling Tower 2'])
    tree.insert('Area A', parent='Cooling Tower 1')
    tree.insert('Area D', parent='Cooling Tower 2')
    tree.insert(['Temperature', 'Humidity'], parent='Area *')
    tree.move('Area *', 'Cooling Tower 1')

    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Cooling Tower 1', 2),
        ('Root >> Cooling Tower 1', 'Area A', 3),
        ('Root >> Cooling Tower 1 >> Area A', 'Humidity', 4),
        ('Root >> Cooling Tower 1 >> Area A', 'Temperature', 4),
        ('Root >> Cooling Tower 1', 'Area D', 3),
        ('Root >> Cooling Tower 1 >> Area D', 'Humidity', 4),
        ('Root >> Cooling Tower 1 >> Area D', 'Temperature', 4),
        ('Root', 'Cooling Tower 2', 2)
    ])

    assert_frame_equal(tree._dataframe, expected)


@pytest.mark.unit
def test_move_errors():
    tree = Tree(pd.DataFrame([{
        'Name': 'Item 1'
    }, {
        'Name': 'Item 2',
        'Path': 'Item 1'
    }, {
        'Name': 'Item 3',
        'Path': 'Item 1 >> Item 2'
    }]))

    with pytest.raises(ValueError, match='Source cannot contain the destination'):
        tree.move('Item 2', 'Item 3')

    with pytest.raises(ValueError, match='Destination must match a single element'):
        tree.move('Item 3', 'Item *')


@pytest.mark.unit
def test_fill_column_values():
    df = pd.DataFrame([{
        'Name': 'Site A_Temp',
        'Unit': '\u00b0F',
        'Facility Type': 'Research Facility'
    }, {
        'Name': 'Site B_Flow',
        'Unit': 'gal/s',
        'Facility Type': 'Factory'
    }])

    queries_to_expected_output = {
        ('{{Name}}',
         '{{Name}}'): pd.Series(['Site A_Temp', 'Site B_Flow']),
        ('{{Name}Site [A-Z]_(.*)}',
         '{{Name}Site ?_(*)}'): pd.Series(['Temp', 'Flow']),
        ('{{Facility Type}} {{Name}Site ([A-Z])_.*}',
         '{{Facility Type}} {{Name}Site (?)_*}'): pd.Series(['Research Facility A', 'Factory B']),
        ('Average of {{Name}(Site [A-Z])_.*} {{Name}Site [A-Z]_(.*)} ({{Unit}})',
         'Average of {{Name}(Site ?)_*} {{Name}Site ?_(*)} ({{Unit}})'): pd.Series(
            ['Average of Site A Temp (\u00b0F)', 'Average of Site B Flow (gal/s)']),
        ('{{Name}(.*_Temp)}',
         '{{Name}(*_Temp)}'): pd.Series(['Site A_Temp', np.nan])
    }

    for (re_query, glob_query), output in queries_to_expected_output.items():
        df['Parent'] = df.apply(_match.fill_column_values, axis=1, query=re_query)
        assert df['Parent'].equals(output)
        df['Parent'] = df.apply(_match.fill_column_values, axis=1, query=glob_query)
        assert df['Parent'].equals(output)


@pytest.mark.unit
def test_insert_with_parent_column():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Area A', 2),
        ('Root >> Area A', 'Optimizer', 3),
        ('Root >> Area A', 'Temperature', 3),
        ('Root', 'Area B', 2),
        ('Root >> Area B', 'Optimizer', 3),
        ('Root >> Area B', 'Temperature', 3),
        ('Root', 'Area C', 2),
        ('Root >> Area C', 'Temperature', 3),
    ])
    tree = Tree('Root')
    tree.insert(['Area A', 'Area B', 'Area C'])
    tree.insert(pd.DataFrame([{
        'Name': 'Optimizer',
        'Type': 'Asset',
        'Parent': r'Area (A|B)'
    }, {
        'Name': 'Temperature',
        'Type': 'Asset',
        'Parent': r'Area \w'
    }]))

    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit
def test_insert_with_column_values():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Factory B', 2),
        ('Root >> Factory B', 'Flow', 3),
        ('Root', 'Research Facility A', 2),
        ('Root >> Research Facility A', 'Site A_Temp', 3)
    ])

    tree = Tree('Root')
    tree.insert(['Research Facility A', 'Factory B'])
    tree.insert(pd.DataFrame([{
        'Name': 'Site A_Temp',
        'Type': 'Asset',
        'Unit': '\u00b0F',
        'Facility Type': 'Research Facility'
    }, {
        'Name': 'Site B_Flow',
        'Type': 'Asset',
        'Unit': 'gal/s',
        'Facility Type': 'Factory'
    }, {
        'Name': 'This item will not have a matching parent',
        'Type': 'Asset'
    }]), friendly_name='{{Name}Site B_(*)}',
        parent='{{Facility Type}} {{Name}Site (?)_*}')

    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit
def test_column_values_non_string_data():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Unit 1', 2),
        ('Root', 'Unit True', 2)
    ])

    tree = Tree('Root')
    children = pd.DataFrame()
    children['Name'] = ['beep', 'bop']
    children['Unit Number'] = [1, True]
    tree.insert(children, friendly_name='Unit {{Unit Number}}')

    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit
def test_insert_parent_dataframe():
    expected_df = _build_dataframe_from_path_name_depth_triples([
        ('', 'Root', 1),
        ('Root', 'Insert Under Me 1st', 2),
        ('Root >> Insert Under Me 1st', '1st Insert', 3),
        ('Root >> Insert Under Me 1st', 'Insert Me Under All', 3),
        ('Root', 'Insert Under Me 2nd', 2),
        ('Root >> Insert Under Me 2nd', '2nd Insert', 3),
        ('Root >> Insert Under Me 2nd', 'Insert Me Under All', 3),
        ('Root', 'Insert Under Me 3rd', 2),
        ('Root >> Insert Under Me 3rd', '3rd Insert', 3),
        ('Root >> Insert Under Me 3rd', 'Insert Me Under All', 3),
        ('Root', 'Insert Under Me 4th', 2),
        ('Root >> Insert Under Me 4th', '4th Insert', 3),
        ('Root >> Insert Under Me 4th', 'Insert Me Under All', 3),
    ])
    sample_id = _common.new_placeholder_guid()
    sample_ref_id = _common.new_placeholder_guid()

    expected_df.loc[expected_df['Name'] == 'Insert Under Me 3rd', 'ID'] = sample_id
    expected_df.loc[expected_df['Name'] == 'Insert Under Me 4th', 'Referenced ID'] = sample_ref_id

    tree = Tree('Root')
    tree.insert([f'Insert Under Me {s}' for s in ('1st', '2nd', '3rd', '4th')])
    # Manually insert ID and Referenced ID -- inserting w/ tree.insert() would require a login
    tree._dataframe.loc[tree._dataframe['Name'] == 'Insert Under Me 3rd', 'ID'] = sample_id
    tree._dataframe.loc[tree._dataframe['Name'] == 'Insert Under Me 4th', 'Referenced ID'] = sample_ref_id

    full_parent_dataframe = pd.DataFrame([{
        # Name case
        'Name': 'Insert Under Me 1st'
    }, {
        # Name + Path case
        'Name': 'Insert Under Me 2nd',
        'Path': 'Root'
    }, {
        # ID case
        'ID': sample_id,
        'Name': 'Doesn\'t matter'
    }, {
        # Referenced ID case
        'ID': sample_ref_id,
        'Name': 'Doesn\'t matter'
    }])
    full_parent_dataframe['Extra Column'] = 'Anything'

    # Perform insertions with `parent` given by a dataframe
    for i, s in enumerate(['1st', '2nd', '3rd', '4th']):
        tree.insert(f'{s} Insert', parent=full_parent_dataframe.iloc[i:i + 1])
    tree.insert('Insert Me Under All', parent=full_parent_dataframe)

    assert_frame_equal(tree._dataframe, expected_df)


@pytest.mark.unit
def test_constructor_with_friendly_name():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'Friendly Root Name', 1),
        ('Friendly Root Name', 'Friendly Item 1 Name', 2),
        ('Friendly Root Name', 'Item 2', 2)
    ])

    data = pd.DataFrame([{
        'Name': 'Root // Friendly Root Name'
    }, {
        'Path': 'Root // Friendly Root Name',
        'Name': 'Item 1 // Friendly Item 1 Name'
    }, {
        'Path': 'Root // Friendly Root Name',
        'Name': 'Item 2'
    }])
    tree = Tree(data, friendly_name='{{Name}*// (*)}')

    assert_frame_equal(tree._dataframe, expected)


@pytest.mark.unit
def test_rename():
    expected = _build_dataframe_from_path_name_depth_triples([
        ('', 'New Root Name', 1),
        ('New Root Name', 'Item 1', 2),
        ('New Root Name >> Item 1', 'Item 2', 3),
        ('New Root Name', 'Item 3', 2)
    ])

    data = pd.DataFrame([{
        'Name': 'Root'
    }, {
        'Path': 'Root',
        'Name': 'Item 1'
    }, {
        'Path': 'Root',
        'Name': 'Item 3'
    }, {
        'Path': 'Root >> Item 1',
        'Name': 'Item 2'
    }])

    tree1 = Tree(data, friendly_name='New Root Name')
    assert_frame_equal(tree1._dataframe, expected)

    tree2 = Tree(data)
    tree2.name = 'New Root Name'
    assert_frame_equal(tree2._dataframe, expected)


@pytest.mark.unit
def test_is_column_value_query():
    assert _match.is_column_value_query('{{Name}}') is True
    assert _match.is_column_value_query('{{Name}(Area ?)_*}') is True
    assert _match.is_column_value_query('{{Facility Type} Factory ([a-zA-Z]{1,20})}') is True
    assert _match.is_column_value_query('{ {Name}(Area ?)_*}') is False
    assert _match.is_column_value_query('{(Area ?)_*{Name}}') is False
    assert _match.is_column_value_query('{Name}') is False
    assert _match.is_column_value_query('Name') is False


@pytest.mark.unit
def test_glob_capture_groups():
    query_asset = '(Area ?)_*'
    query_name = 'Area ?_(*)'

    item = 'Area A_Temperature'

    match = re.match(_match.glob_with_capture_groups_to_regex(query_asset), item)
    assert match is not None
    assert match[1] == 'Area A'

    match = re.match(_match.glob_with_capture_groups_to_regex(query_name), item)
    assert match is not None
    assert match[1] == 'Temperature'

    item = 'Mismatching Item'
    match = re.match(_match.glob_with_capture_groups_to_regex(query_asset), item)
    assert match is None


@pytest.mark.unit
def test_make_paths_from_levels():
    # test that it works when levels but no columns are passed
    df = pd.DataFrame([{
        'Level 1': 'Root',
        'Name': 'Area A',
        'Property': 'Anything',
        'Numerical': 123
    }, {
        'Level 1': 'Root',
        'Level 2': 'Area A',
        'Name': 'Temperature',
        'Property': 'New Value',
        'Numerical': 1
    }, {
        'Level 1': 'Root',
        'Level 2': 'Area A',
        'Name': 'Optimizer',
        'Property': 'Anything',
        'Numerical': 2
    }])
    expected_df = pd.DataFrame([{
        'Path': 'Root',
        'Name': 'Area A',
        'Property': 'Anything',
        'Numerical': 123
    }, {
        'Path': 'Root >> Area A',
        'Name': 'Temperature',
        'Property': 'New Value',
        'Numerical': 1
    }, {
        'Path': 'Root >> Area A',
        'Name': 'Optimizer',
        'Property': 'Anything',
        'Numerical': 2
    }])
    _csv.make_paths_from_levels(df)
    assert_frame_equal(df, expected_df)

    # test that it works when only path is passed
    path = expected_df.copy()
    _csv.make_paths_from_levels(path)
    assert_frame_equal(path, expected_df)

    # test that it works when level and path are provided
    expected_both = pd.DataFrame([{
        'Path': 'Root',
        'Name': 'Area A',
        'Property': 'Anything',
        'Numerical': 123
    }, {
        'Path': 'Root >> Area A',
        'Name': 'Temperature',
        'Property': 'New Value',
        'Numerical': 1
    }, {
        'Path': 'Root >> Area A',
        'Name': 'Optimizer',
        'Property': 'Anything',
        'Numerical': 2
    }])
    both = expected_both.copy()
    _csv.make_paths_from_levels(both)
    assert_frame_equal(both, expected_both)

    # test for warning when neither level nor path is provided
    fail_df = pd.DataFrame([{
        'Name': 'Area A',
        'Property': 'Anything',
        'Numerical': 123
    }, {
        'Name': 'Temperature',
        'Property': 'New Value',
        'Numerical': 1
    }, {
        'Name': 'Optimizer',
        'Property': 'Anything',
        'Numerical': 2
    }])

    with pytest.raises(ValueError):
        _csv.make_paths_from_levels(fail_df)
