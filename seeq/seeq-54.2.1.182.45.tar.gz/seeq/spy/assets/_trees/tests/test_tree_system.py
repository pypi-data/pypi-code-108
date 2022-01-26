import os
import re

import numpy as np
import pandas as pd
import pytest

from seeq import spy
from seeq.sdk import *
from seeq.spy import _common
from seeq.spy.assets import Tree
from seeq.spy.assets._trees import _constants, _csv, _path
from seeq.spy.tests import test_common


def assert_frame_equal(df1, df2):
    # noinspection PyProtectedMember
    return pd._testing.assert_frame_equal(df1.sort_index(axis=1),
                                          df2.sort_index(axis=1),
                                          check_dtype=False)


def setup_module():
    test_common.initialize_sessions()


@pytest.mark.system
def test_double_push_handling_metadata():
    workbook = 'test_double_push_handling_metadata'
    tree_name = f'{workbook}_{_common.new_placeholder_guid()}'
    tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    example_calc = spy.search({'Name': 'Area A_Temperature', 'Datasource ID': 'Example Data'},
                              workbook=spy.GLOBALS_ONLY)
    example_calc_id = example_calc.iloc[0]['ID']
    tree.insert(pd.DataFrame([{
        'Name': 'calc',
        'Type': 'Condition',
        'Formula': '$x > 100',
        'Formula Parameters': [f'x={example_calc_id}']
    }]))
    tree.push()
    tree.push()
    expected = list()
    expected.append({
        'Name': tree_name,
        'Type': 'Asset',
        'Path': '',
        'Push Result': 'Success'
    })
    expected.append({
        'Name': 'calc',
        'Type': 'CalculatedCondition',
        'Formula': '$x > 100',
        'Formula Parameters': {'$x': example_calc_id}
    })


@pytest.mark.system
def test_insert_calculation_regex_several_asset_levels_and_regex_glob_combo():
    workbook = 'test_insert_calculation_regex_several_asset_levels_and_regex_glob_combo'
    tree_name = f'{workbook}_{_common.new_placeholder_guid()}'
    tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    example_calc = spy.search({'Name': 'Area A_Temperature', 'Datasource ID': 'Example Data'},
                              workbook=spy.GLOBALS_ONLY)
    example_calc_id = example_calc.iloc[0]['ID']

    tree.insert('Asset 1')
    tree.insert('Asset 2', parent='Asset 1')
    tree.insert('Asset 3', parent='Asset 2')

    tree.insert(pd.DataFrame([{
        'Name': "Where's Waldo",
        'Formula Parameters': [f'x={example_calc_id}'],
        'Formula': '$x'
    }]), parent='Asset 3')

    tree.insert(None, 'Asset 2', friendly_name='Guess 1 Level', formula_parameters='x=a* >> w*', formula='$x')

    tree.insert(pd.DataFrame([{
        'Name': 'Guess 2 Levels',
        'Formula Parameters': "x=T?[A-Z][a-z]* 2 >> Asset 3|4 >> w*",  # Asset 2 >> Asset 3 >> WW
        'Formula': '$x'
    }]), parent='Asset 1')

    push_result = tree.push()
    calc_id = push_result.loc[4, 'ID']

    expected_result = list()
    expected_result.append({
        'Name': tree_name,
        'Path': '',
        'Type': 'Asset',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Asset 1',
        'Path': tree_name,
        'Type': 'Asset',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Asset 2',
        'Path': f'{tree_name} >> Asset 1',
        'Type': 'Asset',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Asset 3',
        'Path': f'{tree_name} >> Asset 1 >> Asset 2',
        'Type': 'Asset',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': "Where's Waldo",
        'Path': f'{tree_name} >> Asset 1 >> Asset 2 >> Asset 3',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={example_calc_id}'],
        'Formula': '$x',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Guess 1 Level',
        'Path': f'{tree_name} >> Asset 1 >> Asset 2',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={calc_id}'],
        'Formula': '$x',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Guess 2 Levels',
        'Path': f'{tree_name} >> Asset 1',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={calc_id}'],
        'Formula': '$x',
        'Push Result': 'Success'
    })
    assert_dataframe_equals_expected(push_result, expected_result)

    expected_user_facing = list()
    expected_user_facing.append({
        'Name': tree_name,
        'Path': '',
        'Type': 'Asset'
    })
    expected_user_facing.append({
        'Name': 'Asset 1',
        'Path': tree_name,
        'Type': 'Asset'
    })
    expected_user_facing.append({
        'Name': 'Asset 2',
        'Path': f'{tree_name} >> Asset 1',
        'Type': 'Asset'
    })
    expected_user_facing.append({
        'Name': 'Asset 3',
        'Path': f'{tree_name} >> Asset 1 >> Asset 2',
        'Type': 'Asset'
    })
    expected_user_facing.append({
        'Name': "Where's Waldo",
        'Path': f'{tree_name} >> Asset 1 >> Asset 2 >> Asset 3',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={example_calc_id}'],
        'Formula': '$x'
    })
    expected_user_facing.append({
        'Name': 'Guess 1 Level',
        'Path': f'{tree_name} >> Asset 1 >> Asset 2',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={calc_id}'],
        'Formula': '$x'
    })
    expected_user_facing.append({
        'Name': 'Guess 2 Levels',
        'Path': f'{tree_name} >> Asset 1',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={calc_id}'],
        'Formula': '$x'
    })


@pytest.mark.system
def test_insert_calculation_regex_failure_cases():
    workbook = 'test_insert_calculation_regex_failure_cases'
    tree_name = f'test_insert_calculation_regex_failure_cases_{_common.new_placeholder_guid()}'
    tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    example_calc = spy.search({'Name': 'Area A_Temperature', 'Datasource ID': 'Example Data'},
                              workbook=spy.GLOBALS_ONLY)
    example_calc_id = example_calc.iloc[0]['ID']
    tree.insert('Buffer')
    tree.insert('Test Insert Regex', parent='Buffer')

    tree.insert(pd.DataFrame([{
        'Name': 'Same Name',
        'Formula Parameters': [f'x={example_calc_id}'],
        'Formula': '$x'
    }]), parent='Test Insert Regex')

    tree.insert(pd.DataFrame([{
        'Name': 'Same Name 2',
        'Formula Parameters': [f'x={example_calc_id}'],
        'Formula': '$x'
    }]), parent='Test Insert Regex')

    tree.insert(None, 'Test Insert Regex', friendly_name='Same Name 2', formula='$x',
                formula_parameters=[f'x={example_calc_id}'])

    with pytest.raises(RuntimeError, match='matches multiple items in tree'):
        tree.insert(pd.DataFrame([{
            'Name': 'Multiple Matches',
            'Formula Parameters': 'x=same*',
            'Formula': '$x'
        }]), parent='Test Insert Regex')

    with pytest.raises(RuntimeError, match='Formula parameters must be conditions, scalars, or signals.'):
        tree.insert(pd.DataFrame([{
            'Name': 'Guess Only First Asset',
            'Formula Parameters': 'x=test insert r*',
            'Formula': '$x'
        }]), parent='Buffer')

    with pytest.raises(Exception, match='Formula parameter is invalid, missing, or has been removed from tree'):
        tree.insert(pd.DataFrame([{
            'Name': 'Guess End',
            'Formula Parameters': f'x=.* Name$',
            'Formula': '$x'
        }]), parent='Buffer')

    with pytest.raises(Exception, match='Formula parameter is invalid, missing, or has been removed from tree'):
        tree.insert(pd.DataFrame([{
            'Name': 'Insert Invalid ID Param',
            'Formula Parameters': 'x=3F3ECW84G38J389SGH2H93848',
            'Formula': '$x'
        }]), parent='Buffer')


@pytest.mark.system
def test_insert_calculation_regex_glob_test():
    workbook = 'test_insert_calculation_regex_glob_test'
    tree_name = f'test_insert_calculation_regex_glob_test_{_common.new_placeholder_guid()}'
    tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    example_calc = spy.search({'Name': 'Area A_Temperature', 'Datasource ID': 'Example Data'},
                              workbook=spy.GLOBALS_ONLY)
    example_calc_id = example_calc.iloc[0]['ID']
    tree.insert('Test Insert Regex')

    tree.insert(pd.DataFrame([{
        'Name': 'Test Calculation',
        'Formula Parameters': [f'x={example_calc_id}'],
        'Formula': '$x'
    }]), parent='Test Insert Regex')

    tree.insert(pd.DataFrame([{
        'Name': 'Test Glob Notation',
        'Formula Parameters': 'x=test calc*',
        'Formula': '$x'
    }]), parent='Test Insert Regex')

    tree.insert(pd.DataFrame([{
        'Name': 'Test Regex Notation',
        'Formula Parameters': 'x=T?est ?[A-Z][a-z]*',
        'Formula': '$x'
    }]), parent='Test Insert Regex')

    tree.insert(pd.DataFrame([{
        'Name': 'Test Regex Glob Combo',
        'Formula Parameters': 'x=t* C[a-z]lculation',
        'Formula': '$x'
    }]), parent='Test Insert Regex')
    result = tree.push()
    test_calc_id = result.loc[2, 'ID']

    expected_result = list()
    expected_result.append({
        'Name': tree_name,
        'Path': '',
        'Type': 'Asset',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Test Insert Regex',
        'Path': tree_name,
        'Type': 'Asset',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Test Calculation',
        'Path': f'{tree_name} >> Test Insert Regex',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={example_calc_id}'],
        'Formula': '$x',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Test Glob Notation',
        'Path': f'{tree_name} >> Test Insert Regex',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={test_calc_id}'],
        'Formula': '$x',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Test Regex Notation',
        'Path': f'{tree_name} >> Test Insert Regex',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={test_calc_id}'],
        'Formula': '$x',
        'Push Result': 'Success'
    })
    expected_result.append({
        'Name': 'Test Regex Glob Combo',
        'Path': f'{tree_name} >> Test Insert Regex',
        'Type': 'CalculatedSignal',
        'Formula Parameters': [f'x={test_calc_id}'],
        'Formula': '$x',
        'Push Result': 'Success'
    })
    assert_dataframe_equals_expected(result, expected_result)

    expected = list()
    expected.append({
        'Name': tree_name,
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Test Insert Regex',
        'Path': tree_name,
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Test Calculation',
        'Path': f'{tree_name} >> Test Insert Regex',
        'Type': 'CalculatedSignal',
        'Formula Parameters': {'x': example_calc_id},
        'Formula': '$x'
    })
    expected.append({
        'Name': 'Test Glob Notation',
        'Path': f'{tree_name} >> Test Insert Regex',
        'Type': 'CalculatedSignal',
        'Formula Parameters': {'x': 'test calc*'},
        'Formula': '$x'
    })
    expected.append({
        'Name': 'Test Regex Notation',
        'Path': f'{tree_name} >> Test Insert Regex',
        'Type': 'CalculatedSignal',
        'Formula Parameters': {'x': 'T?est ?[A-Z][a-z]*'},
        'Formula': '$x'
    })
    expected.append({
        'Name': 'Test Regex Glob Combo',
        'Path': f'{tree_name} >> Test Insert Regex',
        'Type': 'CalculatedSignal',
        'Formula Parameters': {'x': 't* C[a-z]lculation'},
        'Formula': '$x'
    })
    assert_tree_equals_expected(tree, expected)


@pytest.mark.system
def test_insert_formulas_with_complex_formula_parameters():
    workbook = 'test_insert_formulas_with_complex_formula_parameters'
    tree_name = f'test_insert_formulas_with_complex_formula_parameters_{_common.new_placeholder_guid()}'
    tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    result_a_df = spy.search({'Name': 'Area A_Temperature', 'Datasource ID': 'Example Data'})
    result_b_df = spy.search({'Name': 'Area B_Temperature', 'Datasource ID': 'Example Data'})
    result_c_df = spy.search({'Name': 'Area C_Temperature', 'Datasource ID': 'Example Data'})
    result_a_id = result_a_df.iloc[0]['ID']
    result_b_id = result_b_df.iloc[0]['ID']
    result_c_id = result_c_df.iloc[0]['ID']
    tree.insert('Test Asset')
    tree.insert('Test Asset Child', parent='Test Asset')

    # test formula parameters as list get converted to dict
    tree.insert(pd.DataFrame([{
        'Name': 'Insert By ID',
        'Formula Parameters': [f'x={result_a_id}', f'y={result_b_id}', f'z={result_c_id}'],
        'Formula': '$x + $y + $z'
    }]), parent='Test Asset Child')

    tree.insert(None, 'Test Asset Child', friendly_name='Insert Formula Params List', formula='$a + $b',
                formula_parameters=[f'a={result_a_id}', f'b={result_b_id}'])

    tree.insert(pd.DataFrame([{
        'Name': 'Insert Empty List',
        'Formula Parameters': [],
        'Formula': 'sinusoid()'
    }]), parent='Test Asset Child')

    # test formula parameters as string get converted to dict
    tree.insert(pd.DataFrame([{
        'Name': 'Sibling Name Match',
        'Formula Parameters': 'x=Insert By ID',
        'Formula': '$x + $x + $x'
    }]), parent='Test Asset Child')

    # test formula parameters as empty dict get converted to dict
    tree.insert(pd.DataFrame([{
        'Name': 'Insert empty params',
        'Formula Parameters': {},
        'Formula': 'sinusoid()'
    }]), parent='Test Asset Child')

    # check formula parameters set to NA get handled properly (set to empty dict)
    tree.insert(pd.DataFrame([{
        'Name': 'Insert with NA Params',
        'Formula Parameters': pd.NA,
        'Formula': 'sinusoid()'
    }]), parent='Test Asset Child')

    tree.insert(pd.DataFrame([{
        'Name': 'Insert By Name and Path',
        'Formula Parameters': ['x=Test Asset Child >> Insert By ID', f'z={result_c_id}',
                               f'y={result_b_id}'],
        'Formula': '$x + $z + $x + $z + $x'
    }]), parent='Test Asset')

    expected = list()
    expected.append({
        'Name': tree_name,
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Test Asset',
        'Path': tree_name,
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Test Asset Child',
        'Path': f'{tree_name} >> Test Asset',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Insert By ID',
        'Path': f'{tree_name} >> Test Asset >> Test Asset Child',
        'Type': pd.NA,
        'Formula Parameters': {'x': result_a_id, 'y': result_b_id, 'z': result_c_id},
        'Formula': '$x + $y + $z'
    })
    expected.append({
        'Name': 'Insert Formula Params List',
        'Path': f'{tree_name} >> Test Asset >> Test Asset Child',
        'Type': pd.NA,
        'Formula Parameters': {'a': result_a_id, 'b': result_b_id},
        'Formula': '$a + $b'
    })
    expected.append({
        'Name': 'Insert Empty List',
        'Path': f'{tree_name} >> Test Asset >> Test Asset Child',
        'Type': pd.NA,
        'Formula Parameters': {},
        'Formula': 'sinusoid()'
    })
    expected.append({
        'Name': 'Sibling Name Match',
        'Path': f'{tree_name} >> Test Asset >> Test Asset Child',
        'Type': pd.NA,
        'Formula Parameters': {'x': 'Insert By ID'},
        'Formula': '$x + $x + $x'
    })
    expected.append({
        'Name': 'Insert empty params',
        'Path': f'{tree_name} >> Test Asset >> Test Asset Child',
        'Type': pd.NA,
        'Formula Parameters': {},
        'Formula': 'sinusoid()'
    })
    expected.append({
        'Name': 'Insert with NA Params',
        'Path': f'{tree_name} >> Test Asset >> Test Asset Child',
        'Type': pd.NA,
        'Formula Parameters': pd.NA,
        'Formula': 'sinusoid()'
    })
    expected.append({
        'Name': 'Insert By Name and Path',
        'Path': f'{tree_name} >> Test Asset',
        'Type': pd.NA,
        'Formula Parameters': {'x': 'Test Asset Child >> Insert By ID', 'z': result_c_id,
                               'y': result_b_id},
        'Formula': '$x + $z + $x + $z + $x'
    })
    assert_tree_equals_expected(tree, expected)

    tree.push()
    for i in range(0, len(expected)):
        if pd.isnull(expected[i]['Type']):
            expected[i]['Type'] = 'CalculatedSignal'
    assert_tree_equals_expected(tree, expected)


@pytest.mark.system
def test_create_tree_from_subtree_of_pushed_tree():
    workbook = 'test_create_tree_from_subtree_of_pushed_tree'

    tree1 = Tree('tree1', workbook=workbook, datasource=workbook)
    tree1.insert(spy.search({'Name': 'Cooling Tower 2', 'Path': 'Example', 'Datasource ID': 'Example Data'},
                            workbook=spy.GLOBALS_ONLY))
    tree1.push()

    tree2 = Tree(spy.search({'Name': 'Cooling Tower 2', 'Path': 'tree1', 'Datasource ID': workbook},
                            workbook=workbook),
                 workbook=workbook, datasource=workbook)
    tree2.push()

    df1 = tree1._dataframe
    df2 = tree2._dataframe
    assert len(df2) == len(df1) - 1
    assert not df2.ID.isin(df1.ID).any()
    assert list(df2['Referenced ID']) == list(df1.loc[1:, 'ID'])


@pytest.mark.system
def test_create_new_tree_then_repull_and_edit():
    workbook = 'test_create_new_tree_then_repull_and_edit'
    tree_name = f'{workbook}_{_common.new_placeholder_guid()}'
    tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    tree.insert(['Cooling Tower 1', 'Cooling Tower 2'])
    tree.insert(children=['Area A', 'Area B', 'Area C'], parent='Cooling Tower 1')
    tree.insert(children=['Area E', 'Area F', 'Area G', 'Area H'], parent='Cooling Tower 2')
    tree.insert(children=['Temperature', 'Optimizer', 'Compressor'], parent=3)

    tower1_areas = ['Area A', 'Area B', 'Area C']
    tower2_areas = ['Area E', 'Area F', 'Area G', 'Area H']
    leaves = ['Temperature', 'Optimizer', 'Compressor']

    expected = list()
    expected.append({
        'Name': tree_name,
        'Path': '',
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Cooling Tower 1',
        'Path': tree_name,
        'Type': 'Asset'
    })
    expected.append({
        'Name': 'Cooling Tower 2',
        'Path': tree_name,
        'Type': 'Asset'
    })
    for area in tower1_areas:
        expected.append({
            'Name': area,
            'Path': f'{tree_name} >> Cooling Tower 1',
            'Type': 'Asset'
        })
        for leaf in leaves:
            expected.append({
                'Name': leaf,
                'Path': f'{tree_name} >> Cooling Tower 1 >> {area}',
                'Type': 'Asset'
            })
    for area in tower2_areas:
        expected.append({
            'Name': area,
            'Path': f'{tree_name} >> Cooling Tower 2',
            'Type': 'Asset'
        })
        for leaf in leaves:
            expected.append({
                'Name': leaf,
                'Path': f'{tree_name} >> Cooling Tower 2 >> {area}',
                'Type': 'Asset'
            })
    assert_tree_equals_expected(tree, expected)

    tree.push()
    assert not tree._dataframe['ID'].isnull().values.any(), "Pushing should set the dataframe's ID for all items"
    assert not tree._dataframe['Type'].isnull().values.any(), "Pushing should set the dataframe's Type for all items"
    search_results_df = spy.search({
        'Path': tree_name
    }, workbook=workbook)
    expected.pop(0)  # Since we're searching using Path, the root node won't be retrieved.

    assert_search_results_equals_expected(search_results_df, expected)

    # Pull in the previously-created test_tree_system by name
    tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    original_root_id, original_root_referenced_id = get_root_node_ids(tree)
    assert _common.is_guid(original_root_id), \
        f'Pulled root ID should be a GUID: {original_root_id}'
    assert str(original_root_referenced_id) == str(np.nan), \
        f'Pulled root Reference ID should be {np.nan}: {original_root_referenced_id}'

    expected_existing_items = 1 + 2 + 3 + 4 + (3 * 3) + (4 * 3)
    assert len(tree._dataframe) == expected_existing_items, \
        f'Pulled tree items do not match count: Real={len(tree._dataframe)}, Expected={expected_existing_items}'
    expected_nodes = create_expected_list_from_tree(tree)

    # Add a single node
    tree.insert(children='Area I', parent='Cooling Tower 2')
    expected_nodes.append({
        'Name': 'Area I',
        'Path': f'{tree_name} >> Cooling Tower 2',
        'Type': 'Asset'
    })
    expected_existing_items += 1
    assert_tree_equals_expected(tree, expected_nodes)
    tree.push()
    # The ID column should be fully filled in when the push occurs
    assert not tree._dataframe['ID'].isnull().any()

    # Pull it again, but by ID
    tree2 = Tree(original_root_id, workbook=workbook, datasource=workbook)
    assert len(tree2._dataframe) == expected_existing_items, \
        f'Edited tree items do not match count: Real={len(tree2._dataframe)}, Expected={expected_existing_items}'
    updated_root_id, updated_root_referenced_id = get_root_node_ids(tree2)
    assert original_root_id == updated_root_id, \
        f'Pulled root ID should be the same as before: Original={original_root_id}, Updated={updated_root_id}'
    assert str(original_root_referenced_id) == str(np.nan), \
        f'Pulled root Reference ID should be the same as before: ' \
        f'Original={original_root_referenced_id}, Updated={updated_root_referenced_id}'
    assert_tree_equals_expected(tree2, expected_nodes)


@pytest.mark.system
def test_insert_referenced_single_item():
    # Setup: Find the IDs of actual Example Data items
    items_api = ItemsApi(spy.session.client)
    result = items_api.search_items(filters=['Name==Area A && Datasource ID==Example Data'],
                                    types=['Asset'])  # type: ItemSearchPreviewPaginatedListV1
    assert len(result.items) >= 1, 'There should be at least one global Area A asset'
    area_a_asset = result.items[0].id
    result = items_api.search_items(filters=['Name==Temperature'], types=['StoredSignal'], asset=area_a_asset)
    assert len(result.items) >= 1, 'There should be at least one global Area A Temperature signal'
    area_a_temperature = result.items[0].id

    # Test inserting an item by ID. It should be made into a reference.
    workbook = 'test_insert_referenced_single_item'
    tree_name = f'{workbook}_{_common.new_placeholder_guid()}'
    tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    tree.insert(area_a_temperature)
    expected = [{
        'Name': tree_name,
        'Path': '',
        'Type': 'Asset'
    }, {
        'Referenced ID': area_a_temperature,
        'Name': 'Temperature',
        'Path': tree_name,
        'Type': 'CalculatedSignal',
        'Formula Parameters': {'signal': area_a_temperature},
    }]
    # Formula Parameters': f'signal={area_a_temperature}',
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will result in no change
    tree.insert(area_a_temperature)
    assert_tree_equals_expected(tree, expected)

    # Test inserting a dataframe with a custom name and ID. It too should be made into a reference that is distinct
    # from the previous one.
    df = pd.DataFrame([{'Name': 'Temperature with new name', 'ID': area_a_temperature}])
    tree.insert(df)
    expected.append({
        'Referenced ID': area_a_temperature,
        'Name': 'Temperature with new name',
        'Path': tree_name,
        'Type': 'CalculatedSignal',
        'Formula Parameters': {'signal': area_a_temperature},
    })
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will still result in no change
    tree.insert(df)
    assert_tree_equals_expected(tree, expected)

    # 'Friendly Name' should work in the same way as above.
    df = pd.DataFrame([{'Friendly Name': 'Temperature with friendly name', 'ID': area_a_temperature}])
    tree.insert(df)
    expected.append({
        'Referenced ID': area_a_temperature,
        'Name': 'Temperature with friendly name',
        'Path': tree_name,
        'Type': 'CalculatedSignal',
        'Formula Parameters': {'signal': area_a_temperature},
    })
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will still result in no change
    tree.insert(df)
    assert_tree_equals_expected(tree, expected)


@pytest.mark.system
def test_insert_referenced_tree_item():
    # Setup: Find the IDs of actual Example Data items
    items_api = ItemsApi(spy.session.client)
    result = items_api.search_items(filters=['Name==Area A && Datasource ID==Example Data'], types=['Asset'])
    assert len(result.items) >= 1, 'There should be at least one global Area A asset'
    area_a_asset = result.items[0].id
    result = items_api.search_items(types=['StoredSignal'], asset=area_a_asset, order_by=['Name'])
    assert len(result.items) >= 5, 'There should be at least five global Area A signals'
    area_a_signals = list()
    for item in result.items:
        area_a_signals.append({'Name': item.name, 'ID': item.id})

    workbook = 'test_insert_referenced_single_item'
    tree_name = f'{workbook}_{_common.new_placeholder_guid()}'

    def create_expected_tuples(asset_name):
        expected_items = [{
            'Referenced ID': area_a_asset,
            'Name': asset_name,
            'Path': tree_name,
            'Type': 'Asset'
        }]
        for signal in area_a_signals:
            expected_items.append({
                'Referenced ID': signal['ID'],
                'Name': signal['Name'],
                'Path': f'{tree_name} >> {asset_name}',
                'Type': 'CalculatedSignal',
                'Formula Parameters': {'signal': signal['ID']}
            })
            # 'Formula Parameters': f"signal={signal['ID']}"
        return expected_items

    # Test inserting an asset by ID. It should be made into a reference and children pulled.
    tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    tree.insert(area_a_asset)
    expected = [{
        'Name': tree_name,
        'Path': '',
        'Type': 'Asset'
    }] + create_expected_tuples('Area A')
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will result in no change
    tree.insert(area_a_asset)
    assert_tree_equals_expected(tree, expected)

    # Test inserting a dataframe with a custom name and ID. It too should be made into a reference that is distinct
    # from the previous one.
    df = pd.DataFrame([{'Name': 'Area A with new name', 'ID': area_a_asset}])
    tree.insert(df)
    expected.extend(create_expected_tuples('Area A with new name'))
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will still result in no change
    tree.insert(df)
    assert_tree_equals_expected(tree, expected)

    # 'Friendly Name' should work in the same way as above.
    df = pd.DataFrame([{'Friendly Name': 'Area A with friendly name', 'ID': area_a_asset}])
    tree.insert(df)
    expected.extend(create_expected_tuples('Area A with friendly name'))
    assert_tree_equals_expected(tree, expected)
    # Inserting it again will still result in no change
    tree.insert(df)
    assert_tree_equals_expected(tree, expected)

    # Inserting a mix of names+IDs should automatically figure out which is which. In this case, insert only
    # existing items. The lack of new rows will prove the resolution was successful (although some of the properties
    # will be lost on 'Area A with new name' due to this call no longer being a reference).
    tree.insert(['Area A with new name', area_a_asset])
    assert len(tree._dataframe) == len(expected)


@pytest.mark.system
def test_remove_from_example_data():
    workbook = 'test_remove_from_example_data'
    tree = spy.assets.Tree('Example', workbook=workbook, datasource=workbook, friendly_name=workbook)
    tree.push()

    df = tree._dataframe
    items_to_be_removed = df[(df.Name == 'Cooling Tower 1') | (df.Path.str.contains('Cooling Tower 1'))]

    status = spy.Status()
    tree.remove('Cooling Tower 1', status=status)
    assert status.df.squeeze()['Total Items Removed'] == 57

    df = tree._dataframe
    assert not ((df['Name'] == 'Cooling Tower 1') | (df['Path'].str.contains('Cooling Tower 1'))).any()

    tree.push()

    items_api = ItemsApi(spy.session.client)
    for guid in items_to_be_removed['ID']:
        item_output = items_api.get_item_and_all_properties(id=guid)
        assert item_output.is_archived is True
    for guid in items_to_be_removed['Referenced ID']:
        item_output = items_api.get_item_and_all_properties(id=guid)
        assert item_output.is_archived is False


@pytest.mark.system
def test_comprehension_funcs_on_example_data():
    example = Tree('Example')

    assert example.height == 4
    assert example.size == 76

    counts = example.count()
    expected_counts = {
        'Asset': 14,
        'Signal': 62
    }
    for key in ['Asset', 'Signal']:
        assert counts[key] == expected_counts[key]
        assert example.count(key) == expected_counts[key]
    for key in ['Condition', 'Scalar', 'Formula']:
        assert example.count(key) == 0

    missing_items_dict = example.missing_items('dict')
    area_f = 'Example >> Cooling Tower 2 >> Area F'
    expected_missing_names = ['Compressor Stage', 'Optimizer', 'Relative Humidity', 'Temperature', 'Wet Bulb']
    assert len(missing_items_dict) == 1
    assert area_f in missing_items_dict
    assert len(missing_items_dict[area_f]) == 5
    for name in expected_missing_names:
        assert name in missing_items_dict[area_f]


@pytest.mark.system
def test_constructor_and_insert_tree_dataframe():
    root_name = 'test_constructor_and_insert_tree_dataframe'
    push_results = spy.push(metadata=pd.DataFrame([{
        'Name': root_name,
        'Type': 'Asset'
    }, {
        'Name': 'Leaf',
        'Type': 'Signal',
        'Path': root_name
    }]), workbook=root_name, worksheet=None, datasource=root_name)

    # The input properties (particularly the Referenced ID and Formula information) should come though
    root = {'Name': root_name,
            'Type': 'Asset',
            'Referenced ID': push_results.ID[0],
            'Path': '',
            'Depth': 1}
    signal = {'Name': 'Leaf',
              'Type': 'Signal',
              'Referenced ID': push_results.ID[1],
              'Formula': '$signal',
              'Formula Parameters': {'signal': _common.new_placeholder_guid()},
              'Path': root_name,
              'Depth': 2,
              'Cache Enabled': False}
    expected = pd.DataFrame(columns=_constants.dataframe_columns)
    expected = expected.append([root, signal], ignore_index=True)
    tree = Tree(pd.DataFrame([root, signal]), workbook=root_name, datasource=root_name)
    assert_frame_equal(tree._dataframe, expected)


@pytest.mark.system
def test_move_pushed_items():
    workbook = 'test_move_pushed_items'
    tree = Tree('Example', workbook=workbook, datasource=workbook, friendly_name=workbook)
    tree.push()

    before_df = tree._dataframe.copy()
    tree.move('Area *', destination='Cooling Tower 2')
    after_df = tree._dataframe.copy()

    for _, before_row in before_df.iterrows():
        if re.search(r'Area [A-Z]', _path.get_full_path(before_row)):
            after_row_query = (after_df.Path == before_row.Path.replace('1', '2')) & (after_df.Name == before_row.Name)
            assert len(after_df[after_row_query]) == 1
            after_row = after_df[after_row_query].iloc[0]
            # The following is the key part we are testing. We want the IDs to be reset only for things
            # that were actually moved.
            if 'Cooling Tower 1' in before_row.Path:
                assert pd.isnull(after_row.ID)
            elif 'Cooling Tower 2' in before_row.Path:
                assert _common.is_guid(after_row.ID)


@pytest.mark.system
def test_root_only_asset_tree_visible():
    # Insert a Tree that has no children.
    workbook = 'test_root_only_asset_tree_visible'
    trees_api = TreesApi(spy.client)
    tree = Tree(workbook, workbook=workbook, datasource=workbook)
    tree.push()
    roots = trees_api.get_tree_root_nodes(scoped_to=tree._workbook_id)
    result = [x.name for x in roots.children if workbook == x.name]
    assert len(result) == 1


@pytest.mark.system
def test_modify_existing_spy_tree_with_constructor():
    workbook = 'test_modify_existing_spy_tree_with_constructor'
    tree1 = Tree(pd.DataFrame([{
        'Name': 'root'
    }, {
        'Name': 'leaf 1',
        'Path': 'root >> asset'
    }, {
        'Name': 'leaf 2',
        'Path': 'root >> asset'
    }, {
        'Name': 'leaf 3',
        'Path': 'root >> asset'
    }, {
        'Name': 'leaf 4',
        'Path': 'root >> asset >> asset to be modified'
    }]), workbook=workbook, datasource=workbook)
    tree1.push()

    # Because tree2 will be defined upon the items of tree1, it will pull and modify what we just pushed via tree1.
    # However, the dataframe input will include modifications that we expect to be reflected in the resulting tree
    #  object, so that spy.push doesn't fail to update pre-existing items in certain ways (changing name, path, or
    #  type).

    tree2_df = tree1._dataframe.copy()
    # Change the name of an existing item.
    # We expect the result to be a reference to the old item.
    tree2_df.at[tree2_df.Name == 'leaf 1', 'Name'] = 'new leaf 1 name'
    # Change the path of an existing item.
    # We expect the result to be a reference to the old item.
    tree2_df.at[tree2_df.Name == 'leaf 2', 'Path'] = 'root >> new leaf 2 path'
    # Change the type of an existing item.
    # We expect this to be a fresh item (not a reference) that overwrites the old item when pushed.
    tree2_df.at[tree2_df.Name == 'leaf 3', 'Type'] = 'CalculatedSignal'
    tree2_df.at[tree2_df.Name == 'leaf 3', 'Formula'] = 'sinusoid()'
    # Rename an asset with children.
    # We expect the result to be a reference to the old asset, and all of the new children to be references to old
    # children.
    tree2_df.at[tree2_df.Name == 'asset to be modified', 'Name'] = 'new asset name'
    tree2_df.at[tree2_df.Name == 'leaf 4', 'Path'] = 'root >> asset >> new asset name'
    # Add a new item. We expect the result to be a fresh item.
    tree2_df = tree2_df.append({'Name': 'additional leaf', 'Path': 'root >> asset'}, ignore_index=True)

    tree2 = Tree(tree2_df, workbook=workbook, datasource=workbook)

    def tree1_id(name):
        rows = tree1._dataframe[tree1._dataframe.Name == name]
        if len(rows) != 1:
            raise RuntimeError('tree1 did not push correctly')
        return rows.ID.iloc[0]

    expected_df = pd.DataFrame([
        ['', 'root', 'Asset', tree1_id('root'), np.nan],
        ['root', 'asset', 'Asset', tree1_id('asset'), np.nan],
        ['root >> asset', 'additional leaf', 'Asset', np.nan, np.nan],
        ['root >> asset', 'leaf 3', 'CalculatedSignal', np.nan, np.nan],
        ['root >> asset', 'new asset name', 'Asset', np.nan, tree1_id('asset to be modified')],
        ['root >> asset >> new asset name', 'leaf 4', 'Asset', np.nan, tree1_id('leaf 4')],
        ['root >> asset', 'new leaf 1 name', 'Asset', np.nan, tree1_id('leaf 1')],
        ['root', 'new leaf 2 path', 'Asset', np.nan, np.nan],
        ['root >> new leaf 2 path', 'leaf 2', 'Asset', np.nan, tree1_id('leaf 2')]
    ], columns=['Path', 'Name', 'Type', 'ID', 'Referenced ID'])

    assert_frame_equal(tree2._dataframe[expected_df.columns], expected_df)

    # Assert equal after push as well, except for new IDs
    tree2.push()
    assert list(tree2._dataframe.ID[expected_df.ID.notnull()]) == list(expected_df.ID[expected_df.ID.notnull()])
    columns_no_id = ['Path', 'Name', 'Type', 'Referenced ID']
    assert_frame_equal(tree2._dataframe[columns_no_id], expected_df[columns_no_id])


@pytest.mark.system
def test_pull_calculations():
    area_a_temp_search = spy.search({'Name': 'Area A_Temperature'}, workbook=spy.GLOBALS_ONLY)
    assert len(area_a_temp_search) > 0
    area_a_temp_id = area_a_temp_search.ID[0]

    workbook = 'test_pull_calcs'
    tree_name = f'{workbook}_{_common.new_placeholder_guid()}'
    orig_tree = Tree(tree_name, workbook=workbook, datasource=workbook)
    orig_tree.insert(pd.DataFrame([{
        'Name': 'Calc with Parameters',
        'Formula': '$x + $x',
        'Formula Parameters': [f'x={area_a_temp_id}']
    }, {
        'Name': 'Condition Calc',
        'Formula': 'days()'
    }, {
        'Name': 'Scalar Calc',
        'Formula': '1'
    }, {
        'Name': 'Signal Calc',
        'Formula': 'sinusoid()'
    }]))
    orig_tree.push()
    orig_root_id = orig_tree._dataframe.ID[0]

    expected_df = orig_tree._dataframe.copy()
    expected_df['Cache Enabled'] = False
    for i in (2, 3, 4):
        expected_df.at[i, 'Formula Parameters'] = dict()

    # First pull the same tree without references
    tree1 = Tree(pd.DataFrame([{
        'ID': orig_root_id
    }]), workbook=workbook, datasource=workbook)
    assert_frame_equal(expected_df, tree1._dataframe)

    # Then pull the same tree, but rename the root node so it is forced to become a reference
    tree2 = Tree(pd.DataFrame([{
        'Name': 'New Root Name',
        'ID': orig_root_id
    }]), workbook=workbook, datasource=workbook)
    df = tree2._dataframe.copy()
    assert (df.Path.iloc[1:] == 'New Root Name').all()
    assert df.ID.isnull().all()
    assert list(df['Referenced ID']) == list(expected_df.ID)
    assert list(df['Formula'].iloc[1:]) == ['$signal', '$condition', '$scalar', '$signal']
    assert df['Formula Parameters'].iloc[1:].str.fullmatch(r'[a-z]+\=' + _common.GUID_REGEX).all()

    # Make sure that pulling the same tree but specifying the correct tree does not result in references
    tree3 = Tree(pd.DataFrame([{
        'Name': tree_name,
        'ID': orig_root_id
    }]), workbook=workbook, datasource=workbook)
    assert_frame_equal(expected_df, tree3._dataframe)

    # Pull as references using Referenced ID column
    tree4 = Tree(pd.DataFrame([{
        'Name': tree_name,
        'Referenced ID': orig_root_id
    }]), workbook=workbook, datasource=workbook)
    # Assert that this is equal to tree2 except for the root name change (and a Cache Enabled value)
    df = tree2._dataframe.copy()
    df['Name'] = df['Name'].str.replace('New Root Name', tree_name)
    df['Path'] = df['Path'].str.replace('New Root Name', tree_name)
    df.loc[0, 'Cache Enabled'] = np.nan
    assert_frame_equal(tree4._dataframe, df)


@pytest.mark.system
def test_remove_by_dataframe():
    example_data = spy.search({'Datasource ID': 'Example Data', 'Name': 'Example', 'Type': 'Asset'},
                              workbook=spy.GLOBALS_ONLY)
    workbook = 'test_remove_by_dataframe'
    tree = Tree(example_data, workbook=workbook, datasource=workbook, friendly_name=workbook)

    df = tree._dataframe
    tree_without_cooling_tower_1 = df[(~df['Path'].str.contains('Cooling Tower 1')) & (df['Name'] != 'Cooling Tower 1')]
    tree_without_cooling_tower_1.reset_index(drop=True, inplace=True)

    cooling_tower_1 = spy.search({'Datasource ID': 'Example Data', 'Name': 'Cooling Tower 1', 'Type': 'Asset'},
                                 workbook=spy.GLOBALS_ONLY)
    tree.remove(cooling_tower_1)

    assert_frame_equal(tree._dataframe, tree_without_cooling_tower_1)


@pytest.mark.system
def test_friendly_name_example_data():
    example_data = spy.search([{'Datasource ID': 'Example Data', 'Name': 'Example', 'Type': 'Asset'},
                               {'Datasource ID': 'Example Data', 'Path': 'Example'}],
                              all_properties=True, workbook=spy.GLOBALS_ONLY)
    workbook = 'test_friendly_name_example_data'
    tree = Tree(example_data, friendly_name='{{Type}*Signal*()}{{Asset}}_{{Name}}',
                workbook=workbook, datasource=workbook)

    df = tree._dataframe
    assert ((df['Type'].str.contains('Signal')) == (df['Name'].str.contains('_'))).all()


@pytest.mark.system
def test_csv_validation():
    # csv file that doesn't exist
    name = "midvale.csv"
    message = f"File {name} not found. Please ensure you have it in the correct working directory."
    with pytest.raises(ValueError, match=message):
        Tree(name)

    csv_dir = os.path.join(os.path.dirname(__file__), 'tree_csv_files')

    # csv with missing names
    message = f"Either 'Name' or 'ID' column must be complete, without missing values."
    with pytest.raises(ValueError, match=message):
        Tree(os.path.join(csv_dir, 'missing_names.csv'))

    # csv without a name or ID column
    message = f"A 'Name' or 'ID' column is required"
    with pytest.raises(ValueError, match=message):
        Tree(os.path.join(csv_dir, "no_name_col.csv"))

    # csv without a Level 1 column
    message = f"Levels columns or a path column must be provided"
    with pytest.raises(ValueError, match=message):
        Tree(os.path.join(csv_dir, "no_level1.csv"))


@pytest.mark.system
def test_csv_with_non_unique_names():
    # check for warning when search result should return more than a one-to-one matching
    warning = f"The following names returned multiple search results, so the first result was " \
              f"used: ['Compressor Stage']"
    status = spy.Status()
    csv_dir = os.path.join(os.path.dirname(__file__), 'tree_csv_files')
    Tree(os.path.join(csv_dir, 'multiple_search_results.csv'), status=status)
    assert warning in status.warnings


@pytest.mark.system
def test_csv_with_non_existent_names():
    # check for warning when search result should be missing an item from the csv
    warning = f"The following names did not return search results and were ignored: " \
              f"['Area A_Tempearture']"
    status = spy.Status()
    csv_dir = os.path.join(os.path.dirname(__file__), 'tree_csv_files')
    Tree(os.path.join(csv_dir, 'missing_search_results.csv'), status=status)
    assert warning in status.warnings


@pytest.mark.system
def test_csv_creates():
    csv_dir = os.path.join(os.path.dirname(__file__), 'tree_csv_files')

    # set up the expected dataframe
    signal1_id = _get_first_id_from_signal_name('Area A_Compressor Power')
    signal2_id = _get_first_id_from_signal_name('Area B_Compressor Stage')
    root = {'Name': 'My Root',
            'Type': 'Asset',
            'Path': '',
            'Depth': 1}
    tower1 = {'Name': 'Cooling Tower A',
              'Type': 'Asset',
              'Path': 'My Root',
              'Depth': 2}
    tower2 = {'Name': 'Cooling Tower B',
              'Type': 'Asset',
              'Path': 'My Root',
              'Depth': 2}
    area1 = {'Name': 'Area 1',
             'Type': 'Asset',
             'Path': 'My Root >> Cooling Tower A',
             'Depth': 3}
    area2 = {'Name': 'Area 2',
             'Type': 'Asset',
             'Path': 'My Root >> Cooling Tower B',
             'Depth': 3}
    signal1 = {'Name': 'Area A_Compressor Power',
               'Type': 'CalculatedSignal',
               'Referenced ID': signal1_id,
               'Formula': '$signal',
               'Formula Parameters': {'signal': signal1_id},
               'Path': 'My Root >> Cooling Tower A >> Area 1',
               'Depth': 4,
               'Cache Enabled': False}
    signal2 = {'Name': 'Area B_Compressor Stage',
               'Type': 'CalculatedSignal',
               'Referenced ID': signal2_id,
               'Formula': '$signal',
               'Formula Parameters': {'signal': signal2_id},
               'Path': 'My Root >> Cooling Tower B >> Area 2',
               'Depth': 4,
               'Cache Enabled': False}

    expected = pd.DataFrame(columns=_constants.dataframe_columns)
    expected = expected.append([root, tower1, area1, signal1, tower2, area2, signal2], ignore_index=True)

    # check simplest tree
    tree = Tree(os.path.join(csv_dir, 'simplest.csv'))
    assert_frame_equal(expected, tree._dataframe)

    # write to a csv and read back from it
    filename = 'id_test.csv'
    filename_temp = 'id_test_temp.csv'

    csv_df = pd.read_csv(os.path.join(csv_dir, filename))
    csv_df['ID'] = [signal1_id, signal2_id]
    csv_df.to_csv(os.path.join(csv_dir, filename_temp), index=False)

    tree_id = Tree(os.path.join(csv_dir, filename_temp))
    csv_df['ID'] = ''
    csv_df.to_csv(os.path.join(csv_dir, filename_temp), index=False)

    assert_frame_equal(expected, tree_id._dataframe)
    # Clean up the file that we've written
    os.remove(os.path.join(csv_dir, filename_temp))

    # check that friendly names are used when provided
    # updated expected to use friendly names
    expected.at[3, 'Name'] = 'Compressor Power'
    expected.at[6, 'Name'] = 'Compressor Stage'
    tree_friendly = Tree(os.path.join(csv_dir, 'simple_friendly.csv'))
    assert_frame_equal(expected, tree_friendly._dataframe)

    # check that forward-fill works as expected
    tree_ff = Tree(os.path.join(csv_dir, 'simple_forward_fill.csv'))
    assert_frame_equal(expected, tree_ff._dataframe)


@pytest.mark.system
def test_get_ids_by_name_from_user_input():
    # set up the df to search on
    search1 = {'Name': 'Area A_Compressor Power',
               'Type': 'Signal',
               'Path': 'My Root >> Cooling Tower A >> Area 1',
               'Depth': 4,
               'Cache Enabled': False}
    search2 = {'Name': 'Area B_Compressor Stage',
               'Type': 'Signal',
               'Path': 'My Root >> Cooling Tower B >> Area 2',
               'Depth': 4,
               'Cache Enabled': False}
    search_df = pd.DataFrame()
    search_df = search_df.append([search1, search2], ignore_index=True)
    status = spy.Status()
    results = _csv.get_ids_by_name_from_user_input(search_df, status)

    # set up the expected dataframe
    signal1_id = _get_first_id_from_signal_name('Area A_Compressor Power')
    signal2_id = _get_first_id_from_signal_name('Area B_Compressor Stage')

    signal1 = {'Name': 'Area A_Compressor Power',
               'Type': 'Signal',
               'ID': signal1_id,
               'Path': 'My Root >> Cooling Tower A >> Area 1',
               'Depth': 4,
               'Cache Enabled': False}
    signal2 = {'Name': 'Area B_Compressor Stage',
               'Type': 'Signal',
               'ID': signal2_id,
               'Path': 'My Root >> Cooling Tower B >> Area 2',
               'Depth': 4,
               'Cache Enabled': False}

    expected = pd.DataFrame()
    expected = expected.append([signal1, signal2], ignore_index=True)
    assert_frame_equal(expected, results)


@pytest.mark.system
def test_process_csv_data():
    csv_dir = os.path.join(os.path.dirname(__file__), 'tree_csv_files')
    status = spy.Status()
    results = _csv.process_csv_data(os.path.join(csv_dir, 'simplest.csv'), status)

    signal1_id = _get_first_id_from_signal_name('Area A_Compressor Power')
    signal2_id = _get_first_id_from_signal_name('Area B_Compressor Stage')
    signal1 = {'Level 1': 'My Root',
               'Level 2': 'Cooling Tower A',
               'Level 3': 'Area 1',
               'Name': 'Area A_Compressor Power',
               'ID': signal1_id
               }
    signal2 = {'Level 1': 'My Root',
               'Level 2': 'Cooling Tower B',
               'Level 3': 'Area 2',
               'Name': 'Area B_Compressor Stage',
               'ID': signal2_id
               }

    expected = pd.DataFrame()
    expected = expected.append([signal1, signal2], ignore_index=True)
    assert_frame_equal(expected, results)


@pytest.mark.system
def test_double_push():
    workbook = 'test_double_push'
    tree = Tree('My Root', workbook=workbook, datasource=workbook)
    tree.insert('My Asset')
    tree.insert('My Signal', formula='sinusoid()', parent='My Asset')
    tree.insert('My Condition', formula='days()', parent='My Asset')
    tree.insert('My Scalar', formula='1', parent='My Asset')

    tree.push()
    df_after_first_push = tree._dataframe.copy()

    tree.push()
    df_after_second_push = tree._dataframe.copy()

    assert_frame_equal(df_after_second_push, df_after_first_push)

    search_results = spy.search(df_after_second_push[['ID']], all_properties=True)
    assert_frame_equal(search_results[['Name', 'Type', 'ID', 'Formula']],
                       df_after_second_push[['Name', 'Type', 'ID', 'Formula']])
    pd.testing.assert_series_equal(search_results.apply(_path.determine_path, axis=1),
                                   df_after_second_push['Path'],
                                   check_dtype=False,
                                   check_names=False)


def _get_first_id_from_signal_name(name):
    return spy.search(pd.DataFrame.from_dict({'Name': [name], 'Type': ['Signal']}),
                      workbook=spy.GLOBALS_ONLY, order_by=["ID"])['ID'][0]


def assert_tree_equals_expected(tree, expected_nodes):
    tree_dataframe = tree._dataframe
    assert_dataframe_equals_expected(tree_dataframe, expected_nodes)


def assert_dataframe_equals_expected(tree_dataframe, expected_nodes):
    pd.set_option('display.max_columns', None)  # Print all columns if something errors
    for expected_node in expected_nodes:
        found_series = pd.Series(data=([True] * len(tree_dataframe)))
        for key, value in expected_node.items():
            if pd.isnull(value):
                found_series = found_series & (tree_dataframe[key].isnull())
            elif isinstance(value, list) or isinstance(value, dict):
                found_series = found_series & tree_dataframe[key].apply(lambda x: x == value)
            else:
                found_series = found_series & (tree_dataframe[key] == value)

        assert found_series.sum() == 1, \
            f"Found item {expected_node}" \
            f"\n{found_series.sum()} times in Dataframe" \
            f"\n{tree_dataframe}"
    assert len(tree_dataframe) == len(expected_nodes), \
        f'Tree items do not match count: Real={len(tree_dataframe)}, Expected={len(expected_nodes)}'


def assert_search_results_equals_expected(search_results_df, expected_nodes):
    pd.set_option('display.max_columns', None)  # Print all columns if something errors

    for expected_node in expected_nodes:
        asset = np.nan
        # Extract the parent asset from that path
        if expected_node['Path'].count('>>') > 0:
            asset = expected_node['Path'].rpartition(' >> ')[2]
        elif expected_node['Path'] is not '':
            asset = expected_node['Path']

        node_df = search_results_df[
            (search_results_df['Name'] == expected_node['Name']) &
            (search_results_df['Asset'] == asset) &
            (search_results_df['Type'] == expected_node['Type'])]

        assert len(node_df) == 1, \
            f"Expected item ({expected_node['Name']}, {asset}, {expected_node['Type']})" \
            f"\n was not found in Dataframe" \
            f"\n{search_results_df}"
    assert len(search_results_df) == len(expected_nodes), \
        f'Search result items do not match count: Real={len(search_results_df)}, Expected={len(expected_nodes)}'


def create_expected_list_from_tree(tree):
    # Create a list of node dicts from an existing tree.
    tree_dataframe = tree._dataframe
    expected = list()
    for index, row in tree_dataframe.iterrows():
        expected.append({
            'Name': row['Name'],
            'Path': row['Path'],
            'Type': row['Type']
        })
    return expected


def get_root_node_ids(tree):
    # Get the ID and Reference ID from the tree's root
    tree_dataframe = tree._dataframe
    root_df = tree_dataframe[(tree_dataframe['Path'] == '')]
    assert len(root_df) == 1, \
        f"Exactly one root node was not found in Dataframe: \n{tree_dataframe}"
    id = root_df['ID'].values[0]
    referenced_id = root_df['Referenced ID'].values[0]
    return id, referenced_id
