import re
import tempfile
import uuid
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _common, Session
from seeq.spy.tests import test_common
from seeq.spy.tests.test_common import Sessions
from seeq.spy.workbooks import Topic, Analysis


def setup_module():
    test_common.initialize_sessions()


def _assert_result(df, status):
    assert df.spy.status.df['Result'].drop_duplicates().tolist() == [status]


@pytest.mark.system
def test_simple_search():
    search_results = spy.search({
        'Name': 'Area A_Temper'
    }, workbook=spy.GLOBALS_ONLY)

    assert len(search_results) == 1
    assert search_results.spy.status.df.iloc[0]['Pages'] == 1
    _assert_result(search_results, 'Success')
    assert 'Estimated Sample Period' not in search_results

    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Temper'
    }]), workbook=spy.GLOBALS_ONLY)

    # Nothing will be returned because we use a equal-to comparison when a DataFrame is passed in
    assert len(search_results) == 0
    _assert_result(search_results, 'Success')

    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Temperature'
    }]), workbook=spy.GLOBALS_ONLY)

    assert len(search_results) == 1
    _assert_result(search_results, 'Success')

    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Temperature'
    }]), workbook=spy.GLOBALS_ONLY, all_properties=True)

    assert len(search_results) == 1
    _assert_result(search_results, 'Success')
    assert 'Maximum Interpolation' in search_results.iloc[0]


@pytest.mark.system
def test_search_without_pushed_workbook():
    # This test ensures that spy.search() returns consistent results with and without a pushed default workbook.
    # In older versions, if a default workbook had not been pushed, spy.search() would return results from ANY
    # workbook.

    # Make sure there is only one thing that contains 'Area B_Rel'. It will be the (global) stored signal from the
    # example data.
    search_results = spy.search({
        'Name': 'Area B_Rel'
    })
    assert len(search_results) == 1
    _assert_result(search_results, 'Success')

    # Push a new workbook so that we can push a new signal that is scoped to it
    workbook = Analysis('test_signal_in_another_workbook')
    worksheet = workbook.worksheet('auto-created-worksheet')
    spy.workbooks.push(workbook)

    spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Area B_Rel',
        'Formula': 'sinusoid()'
    }]), workbook=workbook.id, worksheet=worksheet.name)

    search_results = spy.search({
        'Name': 'Area B_Rel'
    })

    # We should still only have one result, since the workbook that we pushed to should be excluded
    assert len(search_results) == 1
    _assert_result(search_results, 'Success')

    # Push should create the default workbook (if it didn't exist)
    spy.push()

    search_results = spy.search({
        'Name': 'Area B_Rel'
    })

    # We should still have the 1 result (the global stored signal), but this time the scope of the search is global +
    # default workbook
    assert len(search_results) == 1
    _assert_result(search_results, 'Success')

    search_results = spy.search({
        'Name': 'Area B_Rel'
    }, workbook=spy.GLOBALS_AND_ALL_WORKBOOKS)

    # We should now have two results since we are searching across ALL workbooks
    assert len(search_results) == 2
    _assert_result(search_results, 'Success')

    # Now push a signal to the default workbook.
    push_df = spy.push(metadata=pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'Area B_Rel',
        'Formula': 'sinusoid()'
    }]))

    try:
        search_results = spy.search({
            'Name': 'Area B_Rel'
        })

        # We should now have two results since we pushed a signal to the default workbook
        assert len(search_results) == 2
        _assert_result(search_results, 'Success')

        search_results = spy.search({
            'Name': 'Area B_Rel'
        }, workbook=spy.GLOBALS_ONLY)

        # We should only have one result because we are searching globals-only
        assert len(search_results) == 1
        _assert_result(search_results, 'Success')

        # Search in a non-existent workbook. This operation would raise an error.
        with pytest.raises(Exception, match='not found'):
            spy.search({
                'Name': 'Area B_Rel'
            }, workbook='My Folder >> folder1 >> Non-existent')

    finally:
        # Rename the pushed signal so that this test can be run multiple times
        items_api = ItemsApi(spy.session.client)
        items_api.set_property(id=push_df.iloc[0]['ID'], property_name='Name',
                               body=PropertyInputV1(value='test_search_without_pushed_workbook_trash'))


@pytest.mark.system
def test_dataframe_single_row_with_id():
    search_results = spy.search({
        'Name': 'Area A_Temper'
    })

    search_results = spy.search(search_results.iloc[0], workbook=spy.GLOBALS_ONLY)

    assert len(search_results) == 1
    assert search_results.iloc[0]['Name'] == 'Area A_Temperature'
    assert search_results.iloc[0]['Data ID'] == '[Tag] Area A_Temperature.sim.ts.csv'
    _assert_result(search_results, 'Success')


@pytest.mark.system
def test_dataframe_multi_row():
    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Relative Humidity',
        'Datasource Name': 'Example Data'
    }, {
        'Name': 'Area A_Temperature',
        'Datasource Name': 'Example Data'
    }, {
        'Path': 'Example >> Cooling Tower 1 >> Area A',
        'Name': 'Relative Humidity'
    }]), workbook=spy.GLOBALS_ONLY)

    assert len(search_results) == 3
    _assert_result(search_results, 'Success')
    assert len(search_results[search_results['Name'] == 'Area A_Temperature']) == 1
    assert len(search_results[search_results['Name'] == 'Area A_Relative Humidity']) == 1
    assert len(search_results[search_results['Name'] == 'Relative Humidity']) == 1


@pytest.mark.system
def test_dataframe_warnings_and_duplicates():
    search_results = spy.search([{
        'Name': 'Humid',
        'Path': 'Example >> Cooling Tower 1'
    }, {
        'Name': 'Area A_',
        'Datasource Name': 'Example Data'
    }, {
        'Name': 'Area A_',
        'Datasource Name': 'Example Data'
    }], workbook=spy.GLOBALS_ONLY)

    # Make sure the duplicates will have been dropped
    assert len(search_results) == 14
    _assert_result(search_results, 'Success')

    assert len(search_results.spy.status.warnings) == 1
    assert '6 duplicates removed' in search_results.spy.status.warnings.pop()

    search_results.drop(columns=['ID'], inplace=True)

    search_results2 = spy.search(search_results, workbook=spy.GLOBALS_ONLY)

    # There will be a warning because 'Value Unit Of Measure' will be part of the DataFrame but it can't be searched on
    assert len(search_results2.spy.status.warnings) == 1
    _assert_result(search_results2, 'Success')
    assert 'are not indexed and will be ignored:\n"Value Unit Of Measure", "Archived"' in \
           search_results2.spy.status.warnings.pop()

    assert len(search_results2) == 14

    unique_ids = search_results2['ID'].drop_duplicates().to_list()
    assert len(unique_ids) == 14


@pytest.mark.system
def test_path_with_datasource():
    search_results = spy.search({
        'Name': 'Area ?_*',
        'Datasource Name': 'Example Data'
    }, workbook=spy.GLOBALS_ONLY)

    push_df = search_results.copy()
    push_df['Reference'] = True
    push_df['Path'] = 'test_path_with_datasource-tree >> branch-alpha'
    push_df['Asset'] = push_df['Name'].str.extract(r'(Area .)_.*')
    push_df['Name'] = push_df['Name'].str.extract(r'Area ._(.*)')

    spy.push(metadata=push_df, datasource='test_path_with_datasource-name-1',
             workbook='test_path_with_datasource', worksheet=None)

    push_df['Path'] = 'test_path_with_datasource-tree >> branch-bravo'

    spy.push(metadata=push_df, datasource='test_path_with_datasource-name-2',
             workbook='test_path_with_datasource', worksheet=None)

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree',
    }, workbook='test_path_with_datasource', recursive=False)

    _assert_result(search_results, 'Success')
    paths = search_results['Path'].drop_duplicates().dropna().tolist()
    assets = search_results['Asset'].drop_duplicates().tolist()
    names = sorted(search_results['Name'].tolist())
    types = search_results['Type'].drop_duplicates().tolist()

    assert len(paths) == 0
    assert assets == ['test_path_with_datasource-tree']
    assert names == ['branch-alpha', 'branch-bravo']
    assert types == ['Asset']

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree',
    }, workbook='test_path_with_datasource', recursive=True)

    assert len(search_results) > 100
    _assert_result(search_results, 'Success')
    types = sorted(search_results['Type'].drop_duplicates().tolist())
    assert types == ['Asset', 'CalculatedSignal']
    assert len(search_results[search_results['Asset'] == 'branch-alpha']) > 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) > 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree >> branch-alpha',
    }, workbook='test_path_with_datasource', recursive=True)

    assert len(search_results[search_results['Asset'] == 'branch-alpha']) > 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) == 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree >> branch-*',
    }, workbook='test_path_with_datasource', recursive=True)

    assert len(search_results[search_results['Asset'] == 'branch-alpha']) > 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) > 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-* >> branch-bravo',
    }, workbook='test_path_with_datasource', recursive=True)

    assert len(search_results[search_results['Asset'] == 'branch-alpha']) == 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) > 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-* >> branch-bravo',
        'Datasource Name': 'test_path_with_datasource-name-1'
    }, workbook='test_path_with_datasource', recursive=True)

    assert len(search_results) == 0

    search_results = spy.search({
        'Path': 'test_path_with_datasource-* >> branch-alpha',
        'Datasource Name': 'test_path_with_datasource-name-1'
    }, workbook='test_path_with_datasource', recursive=True)

    assert len(search_results[search_results['Asset'] == 'branch-alpha']) > 0
    assert len(search_results[search_results['Asset'] == 'branch-bravo']) == 0


@pytest.mark.system
def test_dataframe_bad_datasource():
    with pytest.raises(RuntimeError):
        spy.search(pd.DataFrame([{
            'Name': 'Area A_Temperature',
            'Datasource Name': 'Bad Datasource'
        }]), workbook=spy.GLOBALS_ONLY)


@pytest.mark.system
def test_type_search():
    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Signal'
    }, workbook=spy.GLOBALS_ONLY)

    assert 150 < len(search_results) < 230
    _assert_result(search_results, 'Success')

    datasource_names = set(search_results['Datasource Name'].tolist())
    assert len(datasource_names) == 1
    assert datasource_names.pop() == 'Example Data'

    types = set(search_results['Type'].tolist())
    assert len(types) == 1
    assert types.pop() == 'StoredSignal'

    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Condition'
    }, workbook=spy.GLOBALS_ONLY)

    assert len(search_results) == 0
    _assert_result(search_results, 'Success')

    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Scalar'
    }, workbook=spy.GLOBALS_ONLY)

    assert len(search_results) == 0
    _assert_result(search_results, 'Success')

    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': 'Asset'
    }, workbook=spy.GLOBALS_ONLY)

    assert 5 < len(search_results) < 20
    _assert_result(search_results, 'Success')

    # Multiple types
    search_results = spy.search({
        'Datasource Class': 'Time Series CSV Files',
        'Type': ['Signal', 'Asset']
    }, workbook=spy.GLOBALS_ONLY)

    _assert_result(search_results, 'Success')
    assert 160 < len(search_results) < 300
    assert 5 < len(search_results[search_results['Type'] == 'Asset']) < 20
    assert 150 < len(search_results[search_results['Type'].str.contains('Signal')]) < 230


@pytest.mark.system
def test_path_search_recursive():
    search_results = spy.search({
        'Path': 'Non-existent >> Path'
    }, workbook=spy.GLOBALS_ONLY)

    assert len(search_results) == 0
    _assert_result(search_results, 'Success')

    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1'
    }, workbook=spy.GLOBALS_ONLY)

    assert 40 < len(search_results) < 60
    _assert_result(search_results, 'Success')

    search_results = spy.search({
        'Path': '*xamp* >> Cooling Tower *',
        'Name': '*Compressor*'
    }, workbook=spy.GLOBALS_ONLY)

    _assert_result(search_results, 'Success')
    names = search_results['Name'].drop_duplicates().tolist()
    assert len(names) == 2
    assert 'Compressor Power' in names
    assert 'Compressor Stage' in names
    paths = search_results['Path'].drop_duplicates().tolist()
    assert len(paths) == 2
    assert 'Example >> Cooling Tower 1' in paths
    assert 'Example >> Cooling Tower 2' in paths

    search_results = spy.search({
        'Path': 'Example >> /Cooling Tower [2]/',
        'Name': '*Compressor*'
    }, workbook=spy.GLOBALS_ONLY)

    _assert_result(search_results, 'Success')
    names = search_results['Name'].drop_duplicates().tolist()
    assert len(names) == 2
    assert 'Compressor Power' in names
    assert 'Compressor Stage' in names
    paths = search_results['Path'].drop_duplicates().tolist()
    assert len(paths) == 1
    assert 'Example >> Cooling Tower 2' in paths


@pytest.mark.system
def test_path_search_non_recursive():
    search_results = spy.search({
        'Path': 'Exampl',
        'Type': 'Asset'
    }, workbook=spy.GLOBALS_ONLY, recursive=None)

    assert len(search_results) == 0
    _assert_result(search_results, 'Success')

    search_results = spy.search({
        'Path': 'Example',
        'Type': 'Asset'
    }, workbook=spy.GLOBALS_ONLY, recursive=None)

    assert len(search_results) == 2
    _assert_result(search_results, 'Success')

    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1',
        'Name': '/Area [ABC]/'
    }, workbook=spy.GLOBALS_ONLY, recursive=False)

    assert len(search_results) == 3
    _assert_result(search_results, 'Success')
    types = search_results['Type'].drop_duplicates().tolist()
    assert len(types) == 1
    assert types[0] == 'Asset'

    search_results = spy.search({
        'Path': 'Example >> Cooling Tower *',
        'Asset': 'Area A',
        'Name': '*Compressor*'
    }, workbook=spy.GLOBALS_ONLY, recursive=False)

    assert len(search_results) == 2
    _assert_result(search_results, 'Success')
    names = search_results['Name'].tolist()
    assert len(names) == 2
    assert 'Compressor Power' in names
    assert 'Compressor Stage' in names
    paths = search_results['Path'].drop_duplicates().tolist()
    assert len(paths) == 1
    assert paths[0] == 'Example >> Cooling Tower 1'


@pytest.mark.system
def test_path_search_pagination():
    session = test_common.get_session(Sessions.test_path_search_pagination)
    # This tests the 'Path' finding code to make sure we'll find a path even if pagination
    # is required.
    session.options.search_page_size = 1
    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1 >> Area G'
    }, workbook=spy.GLOBALS_ONLY, recursive=False, session=session)

    assert len(search_results) == 6
    _assert_result(search_results, 'Success')
    assert search_results.spy.status.df.iloc[0]['Count'] == 6
    assert search_results.spy.status.df.iloc[0]['Pages'] == 7


@pytest.mark.system
def test_path_search_root_only():
    search_results = spy.search(pd.DataFrame({
        'Path': [''],
        'Name': ['Example'],
        'Type': ['Asset']
    }), workbook=spy.GLOBALS_ONLY, recursive=False)

    assert len(search_results) == 1
    _assert_result(search_results, 'Success')
    assert search_results.iloc[0]['Name'] == 'Example'
    assert search_results.iloc[0]['Type'] == 'Asset'
    assert 'Path' not in search_results.columns
    assert 'Asset' not in search_results.columns


@pytest.mark.system
def test_asset_id_search():
    search_results = spy.search({
        'Path': 'Example >> Cooling Tower 1',
        'Type': 'Asset'
    }, workbook=spy.GLOBALS_ONLY)

    _assert_result(search_results, 'Success')
    asset_id = search_results[search_results['Name'] == 'Area C'].iloc[0]['ID']

    asset_search = spy.search({'Asset': asset_id}, workbook=spy.GLOBALS_ONLY)

    assert len(asset_search) > 1
    _assert_result(asset_search, 'Success')
    assert all([a == 'Area C' for a in asset_search['Asset'].tolist()])

    asset_search = spy.search({'Asset': asset_id, 'Name': 'Temperature'},
                              workbook=spy.GLOBALS_ONLY)

    assert len(asset_search) == 1
    _assert_result(asset_search, 'Success')
    asset = asset_search.iloc[0]
    assert asset['Asset'] == 'Area C'
    assert asset['Name'] == 'Temperature'


@pytest.mark.system
def test_datasource_name_search():
    with pytest.raises(RuntimeError):
        spy.search({
            'Datasource Name': 'Non-existent'
        }, workbook=spy.GLOBALS_ONLY)

    search_results = spy.search({
        'Datasource Name': 'Example Data'
    }, workbook=spy.GLOBALS_ONLY)

    assert 150 < len(search_results) < 245
    _assert_result(search_results, 'Success')


@pytest.mark.system
def test_search_pagination():
    session = test_common.get_session(Sessions.test_search_pagination)
    session.options.search_page_size = 2
    search_results = spy.search({
        'Name': 'Area A_*'
    }, workbook=spy.GLOBALS_ONLY, session=session)

    assert len(search_results) == 6
    assert search_results.spy.status.df.iloc[0]['Pages'] == 4
    _assert_result(search_results, 'Success')


@pytest.mark.system
def test_search_bad_workbook():
    with pytest.raises(RuntimeError):
        spy.search({
            'Name': 'Area A_*'
        }, workbook='bad')


@pytest.mark.system
def test_search_workbook_guid():
    # The workbook won't be found, so we'll get an access error
    with pytest.raises(ApiException):
        spy.search({
            'Name': 'Area A_*'
        }, workbook='A0B89103-E95D-4E32-A809-390C1FAE9D2F')


@pytest.mark.system
def test_include_archived():
    metadata_df = pd.DataFrame([{
        'Type': 'Signal',
        'Name': 'test_include_archived 1'
    }, {
        'Type': 'Signal',
        'Name': 'test_include_archived 2'
    }])
    metadata_df['Archived'] = True
    workbook = 'test_include_archived'
    push_df = spy.push(metadata=metadata_df, workbook=workbook, worksheet=None, datasource=workbook)

    search_df = spy.search({'Name': 'test_include_archived*', 'Scoped To': push_df.spy.workbook_id})
    assert len(search_df) == 0
    _assert_result(search_df, 'Success')
    search_df = spy.search({'Name': 'test_include_archived*', 'Scoped To': push_df.spy.workbook_id},
                           include_archived=True)
    assert len(search_df) == len(metadata_df)
    _assert_result(search_df, 'Success')

    with pytest.raises(ValueError):
        spy.search({'Path': 'Example', 'Datasource ID': 'Example Data'},
                   workbook=spy.GLOBALS_ONLY, recursive=False, include_archived=True)


@pytest.mark.system
def test_simple_search_with_estimated_sample_period():
    search_results = spy.search({
        'Name': 'Area A_Temper'
    }, workbook=spy.GLOBALS_ONLY, estimate_sample_period=dict(Start=None, End=None))

    assert len(search_results) == 1
    _assert_result(search_results, 'Success')
    assert 'Estimated Sample Period' in search_results
    assert (search_results['Estimated Sample Period'].map(type) == pd.Timedelta).all()

    search_results = spy.search(pd.DataFrame([{'Name': 'Area A_Temperature'}]),
                                workbook=spy.GLOBALS_ONLY,
                                estimate_sample_period=dict(Start='2018-01-01T00:00:00.000Z',
                                                            End='2018-06-01T00:00:00.000Z'))

    assert len(search_results) == 1
    _assert_result(search_results, 'Success')
    assert 'Estimated Sample Period' in search_results
    assert (search_results['Estimated Sample Period'].map(type) == pd.Timedelta).all()
    assert search_results.at[0, 'Estimated Sample Period'] == pd.to_timedelta(120.0, unit='s')


@pytest.mark.system
def test_dataframe_with_estimated_sample_period():
    search_results = spy.search(pd.DataFrame([{
        'Name': 'Area A_Relative Humidity',
        'Datasource Name': 'Example Data'
    }, {
        'Name': 'Area A_Temperature',
        'Datasource Name': 'Example Data'
    }, {
        'Path': 'Example >> Cooling Tower 1 >> Area A',
        'Name': 'Relative Humidity'
    }]), workbook=spy.GLOBALS_ONLY, estimate_sample_period=dict(Start=None, End=None))

    assert len(search_results) == 3
    _assert_result(search_results, 'Success')
    assert 'Estimated Sample Period' in search_results
    assert (search_results['Estimated Sample Period'].map(type) == pd.Timedelta).all()


@pytest.mark.system
def test_path_with_datasource_and_estimated_sample_period():
    search_results = spy.search({
        'Name': 'Area ?_*',
        'Datasource Name': 'Example Data'
    }, workbook=spy.GLOBALS_ONLY)

    assert 'Estimated Sample Period' not in search_results
    push_df = search_results.copy()
    push_df['Reference'] = True
    push_df['Path'] = 'test_path_with_datasource-tree >> branch-alpha'
    push_df['Asset'] = push_df['Name'].str.extract(r'(Area .)_.*')
    push_df['Name'] = push_df['Name'].str.extract(r'Area ._(.*)')

    spy.push(metadata=push_df, datasource='test_path_with_datasource-name-1',
             workbook='test_path_with_datasource_and_estimated_sample_period', worksheet=None)
    push_df['Path'] = 'test_path_with_datasource-tree >> branch-bravo'
    spy.push(metadata=push_df, datasource='test_path_with_datasource-name-2',
             workbook='test_path_with_datasource_and_estimated_sample_period', worksheet=None)

    search_results = spy.search({
        'Path': 'test_path_with_datasource-tree',
    }, workbook='test_path_with_datasource_and_estimated_sample_period',
        recursive=False, estimate_sample_period=dict(Start=None, End=None))

    assert len(search_results) == 2
    _assert_result(search_results, 'Success')
    assert 'Estimated Sample Period' in search_results
    assert search_results['Type'].values[0] == 'Asset' and pd.isna(search_results.at[0, 'Estimated Sample Period'])


@pytest.mark.system
def test_not_enough_data_for_estimated_sample_period():
    search_results = spy.search({
        'Name': 'Area ?_*',
        'Datasource Name': 'Example Data'
    },
        workbook=spy.GLOBALS_ONLY,
        estimate_sample_period=dict(Start='2018-01-01T01:00:00.000Z', End='2018-01-01T02:00:00.000Z'))
    assert 'Estimated Sample Period' in search_results
    _assert_result(search_results, 'Success')
    area_f_compressor_power = search_results[search_results['Name'] == 'Area F_Compressor Power'].squeeze()
    assert pd.isna(area_f_compressor_power['Estimated Sample Period'])


@pytest.mark.system
def test_estimated_sample_period_incorrect_capitalization():
    with pytest.raises(ValueError, match=r"estimate_sample_period must have 'Start' and 'End' keys but got "
                                         r"dict_keys\(\['start', 'End'\]\)"):
        spy.search({
            'Name': 'Area ?_*',
            'Datasource Name': 'Example Data'
        },
            workbook=spy.GLOBALS_ONLY,
            estimate_sample_period=dict(start='2018-01-01T01:00:00.000Z', End='2018-01-01T02:00:00.000Z'))

    with pytest.raises(ValueError, match=r"estimate_sample_period must have 'Start' and 'End' keys but got "
                                         r"dict_keys\(\['Start', 'end'\]\)"):
        spy.search({
            'Name': 'Area ?_*',
            'Datasource Name': 'Example Data'
        },
            workbook=spy.GLOBALS_ONLY,
            estimate_sample_period=dict(Start='2018-01-01T01:00:00.000Z', end='2018-01-01T02:00:00.000Z'))


@pytest.mark.system
def test_search_with_url():
    workbook = test_common.create_worksheet_for_url_tests('test_search_with_url')
    search_results = spy.search(workbook.url, workbook=spy.GLOBALS_ONLY)

    assert len(search_results) == 3
    _assert_result(search_results, 'Success')
    assert search_results[search_results['Name'] == 'Temperature Minus 5']['Type'].values[0] == 'CalculatedSignal'
    assert search_results[search_results['Name'] == 'Cold']['Type'].values[0] == 'CalculatedCondition'
    assert search_results[search_results['Name'] == 'Constant']['Type'].values[0] == 'CalculatedScalar'

    search_results = spy.search(workbook.url, workbook=spy.GLOBALS_ONLY,
                                estimate_sample_period=dict(Start='2018-01-01T00:00:00.000Z',
                                                            End='2018-06-01T00:00:00.000Z'))
    assert 'Estimated Sample Period' in search_results


@pytest.mark.system
def test_search_quiet_flag_with_url():
    workbook = test_common.create_worksheet_for_url_tests('test_search_quiet_flag_with_url')
    warning = "The quiet flag is ignored when a status object is provided. Instead, use the quiet flag of your status " \
              "object by creating a quiet status with spy.Status(quiet=True), or setting status.quiet=True."

    # Test that there is no warning when a status is provided and the quiet flag is not set
    test_status_no_warn = spy.Status()
    _ = spy.search(workbook.url, status=test_status_no_warn)
    assert warning not in test_status_no_warn.warnings

    # Test that there is a warning when both a status is provided and the quiet flag is True
    test_status_warn = spy.Status()
    _ = spy.search(workbook.url, quiet=True, status=test_status_warn)

    assert warning in test_status_warn.warnings


@pytest.mark.system
def test_search_with_url_wrong_url():
    test_common.create_worksheet_for_url_tests('test_search_with_url_wrong_url')
    # test for invalid URLs
    with pytest.raises(ValueError, match=r"The supplied URL is not a valid Seeq address. Verify that both the "
                                         r"workbook ID and worksheet ID are valid Seeq references"):
        spy.search('http://localhost:34216/workbook/376F44F5-9243-A0CF/worksheet/2B7F2EC3-C484-49C6-9FEB-EDA68B9350B1')

    with pytest.raises(ValueError, match=r"The supplied URL is not a valid Seeq address. Verify that both the "
                                         r"workbook ID and worksheet ID are valid Seeq references"):
        spy.search('http://localhost:34216/workbook/376F44F5-9243-453C-A0CF-F14CB08B76FD/worksheet/2B7F2EC3-C484-49C6')

    workbook_id = str(uuid.uuid1()).upper()
    worksheet_id = str(uuid.uuid1()).upper()
    url = f'http://localhost:34216/workbook/{workbook_id}/worksheet/{worksheet_id}'
    with pytest.raises(RuntimeError, match=f'Could not find workbook with ID "{workbook_id}"'):
        spy.search(url)

    host = spy.session.public_url
    workbook_search = spy.workbooks.search({'Name': 'test_search_with_url_wrong_url'})
    workbook = spy.workbooks.pull(workbook_search, include_referenced_workbooks=False, include_inventory=False)[0]
    with pytest.raises(RuntimeError, match=f'Worksheet with ID "{worksheet_id}" does not exist'):
        spy.search(f'{host}/workbook/{workbook.id}/worksheet/{worksheet_id}')


@pytest.mark.system
def test_search_with_url_archived_workbook_worksheet():
    # Get a workbook/worksheet URL for tests
    test_common.create_worksheet_for_url_tests('test_search_with_url_archived_workbook_worksheet')
    workbook_search = spy.workbooks.search({'Name': 'test_search_with_url_archived_workbook_worksheet'})
    workbook = spy.workbooks.pull(workbook_search, include_referenced_workbooks=False, include_inventory=False)[0]
    worksheet = [x for x in workbook.worksheets if x.name == 'search from URL'][0]

    items_api = ItemsApi(spy.session.client)
    items_api.set_property(id=workbook.id, property_name='Archived', body=PropertyInputV1(value=True))

    # tests for archived workbooks
    with pytest.raises(ValueError, match=f"Workbook '{workbook.id}' is archived. Supply 'include_archive=True' if"
                                         f"you want to retrieve the items of an archived workbook"):
        spy.search(workbook.url)

    search_results = spy.search(workbook.url, include_archived=True)
    assert len(search_results) == 3
    _assert_result(search_results, 'Success')

    # unarchive it in case we need it for another test
    items_api.set_property(id=workbook.id, property_name='Archived', body=PropertyInputV1(value=False))

    # tests for archived worksheet
    items_api.set_property(id=worksheet.id, property_name='Archived', body=PropertyInputV1(value=True))
    with pytest.raises(ValueError, match=f"Worksheet '{worksheet.id}' is archived. Supply 'include_archive=True' if"
                                         f"you want to retrieve archived items"):
        spy.search(workbook.url)

    # unarchive it in case we need it for another test
    items_api.set_property(id=worksheet.id, property_name='Archived', body=PropertyInputV1(value=False))


@pytest.mark.system
def test_search_of_topic_url():
    host = spy.session.public_url
    topic = Topic({'Name': "test_Topic_search_url"})
    document = topic.document('Doc1')
    spy.workbooks.push(topic)

    with pytest.raises(ValueError, match=f'URL must be for a valid Workbench Analysis. '
                                         f'You supplied a URL for a Topic.'):
        spy.search(f'{host}/workbook/{topic.id}/worksheet/{document.id}')


@pytest.mark.system
def test_search_kwargs_and_status_metadata():
    search_results = spy.search({'Name': 'Area A_Temperature'}, workbook=spy.GLOBALS_ONLY)
    with tempfile.TemporaryDirectory() as dir_path:
        search_results.to_pickle(str(Path(dir_path, 'search.pkl')))
        search_unpickle = pd.read_pickle(Path(dir_path, 'search.pkl'))
        assert search_unpickle.spy.func == 'spy.search'
        assert search_unpickle.spy.kwargs['query'] == {'Name': 'Area A_Temperature'}
        assert not search_unpickle.spy.kwargs['all_properties']
        assert search_unpickle.spy.kwargs['recursive']
        assert not search_unpickle.spy.kwargs['include_archived']
        assert search_unpickle.spy.kwargs['estimate_sample_period'] is None
        assert isinstance(search_unpickle.spy.status, spy.Status)

        # take a slice of the DataFrame to make sure the metadata is preserved
        search_manipulated = search_unpickle[['ID']]
        assert search_manipulated.spy.kwargs['query'] == {'Name': 'Area A_Temperature'}

    search_results = spy.search({'Name': 'Area A_Temperature'},
                                workbook=spy.GLOBALS_ONLY,
                                estimate_sample_period=dict(Start='2018-01-01T01:00:00.000Z',
                                                            End='2018-01-01T02:00:00.000Z'))
    _assert_result(search_results, 'Success')

    with tempfile.TemporaryDirectory() as dir_path:
        search_results.to_pickle(str(Path(dir_path, 'search.pkl')))
        search_unpickle = pd.read_pickle(Path(dir_path, 'search.pkl'))
        assert search_unpickle.spy.func == 'spy.search'
        assert search_unpickle.spy.kwargs['estimate_sample_period']['Start'] == '2018-01-01T01:00:00.000Z'
        assert search_unpickle.spy.kwargs['estimate_sample_period']['End'] == '2018-01-01T02:00:00.000Z'

        # create a copy of the search DataFrame and test the metadata is preserved on the copy
        duplicate = search_unpickle.copy()
        assert duplicate.spy.kwargs['estimate_sample_period']['Start'] == '2018-01-01T01:00:00.000Z'
        assert duplicate.spy.kwargs['estimate_sample_period']['End'] == '2018-01-01T02:00:00.000Z'


@pytest.mark.system
def test_ignore_unindexed_properties():
    with pytest.raises(ValueError, match=r'The following properties are not indexed:\n"Bilbo"\nUse any of .*'):
        spy.search({
            'Name': 'Area A_Temperature',
            'Bilbo': 'Baggins'
        }, workbook=spy.GLOBALS_ONLY, ignore_unindexed_properties=False)

    search_df = spy.search({
        'Name': 'Area A_Temperature',
        'Bilbo': 'Baggins'
    }, workbook=spy.GLOBALS_ONLY)

    assert len(search_df.spy.status.warnings) == 1
    _assert_result(search_df, 'Success')
    assert search_df.spy.status.warnings.pop().startswith(
        'The following properties are not indexed and will be ignored:\n"Bilbo"')


@pytest.mark.system
def test_order_by():
    _test_order_by_internal(spy.session)


def _test_order_by_internal(session: Session):
    # test each of "ID", "Name", "Description"

    # test ID as a list
    query = {'Name': 'Compressor'}
    id_results = spy.search(query, order_by=['ID'], workbook=spy.GLOBALS_ONLY, session=session)
    _assert_result(id_results, 'Success')
    id_list = list(id_results['ID'])
    assert id_list == sorted(id_list)
    assert id_results.spy.status.df.iloc[0]['Pages'] == int(len(id_results) / session.options.search_page_size) + 1

    # test ID as a string
    id_str_results = spy.search(query, order_by='ID', workbook=spy.GLOBALS_ONLY, session=session)
    _assert_result(id_str_results, 'Success')
    id_str_list = list(id_str_results['ID'])
    assert id_str_list == sorted(id_str_list)

    # Name
    name_results = spy.search(query, order_by=['Name'], workbook=spy.GLOBALS_ONLY, session=session)
    _assert_result(name_results, 'Success')
    name_list = list(name_results['Name'])
    assert name_list == sorted(name_list)

    # Description
    descript_results = spy.search(query, order_by=['Description'], workbook=spy.GLOBALS_ONLY, session=session)
    _assert_result(descript_results, 'Success')
    descript_list = list(descript_results['Description'].dropna())
    assert descript_list == sorted(descript_list)

    # test order_by works for multiple fields
    # if ["ID", "Name"] - should just be sorted by ID
    results = spy.search(query, order_by=['ID', 'Name'], workbook=spy.GLOBALS_ONLY, session=session)
    _assert_result(results, 'Success')
    id_list_2 = list(results['ID'])
    assert id_list_2 == sorted(id_list_2)

    # if ["Name", "ID"] - should be sorted by name and within same name, sorted by ID
    name_id_results = spy.search(query, order_by=['Name', 'ID'], workbook=spy.GLOBALS_ONLY, session=session)
    _assert_result(name_id_results, 'Success')
    copy_results = name_id_results.copy()
    copy_results = copy_results.sort_values(by=['Name', 'ID'])
    assert list(name_id_results['ID']) == list(copy_results['ID'])


@pytest.mark.system
def test_order_by_validation():
    query = {'Name': 'Compressor'}

    # test order_by validation works
    # test if order_by not a list or string
    with pytest.raises(TypeError, match="Argument 'order_by' should be type str or list, but is type int"):
        spy.search(query, order_by=3, workbook=spy.GLOBALS_ONLY)

    # test if order_by contains something other than "Name", "ID", "Description"
    # test with no valid field in list
    message = re.escape("Invalid order_by fields: ['Type']. Search results can only be ordered on ['ID', 'Name', "
                        "'Description'] fields.")
    with pytest.raises(ValueError, match=message):
        spy.search(query, order_by=['Type'], workbook=spy.GLOBALS_ONLY)

    # test with some valid field in list
    with pytest.raises(ValueError, match=message):
        spy.search(query, order_by=['Name', 'Type'], workbook=spy.GLOBALS_ONLY)

    # test with invalid string
    with pytest.raises(ValueError, match=message):
        spy.search(query, order_by='Type', workbook=spy.GLOBALS_ONLY)


@pytest.mark.system
def test_order_by_page_size():
    session = test_common.get_session(Sessions.test_order_by_page_size)

    # test it is correctly ordered if search_page_size < items

    # set search page size low
    session.options.search_page_size = 2
    # use the same tests as in test_order_by() with new config settings
    _test_order_by_internal(session)


@pytest.mark.system
def test_empty_query():
    # This can happen if the user imports a CSV file full of tag names into a DataFrame but the CSV file doesn't
    # have a header.
    query_df = pd.DataFrame({
        'DC3STEAMSO.INITIAL_VALUE': [
            'DC3STEAMSO.FINAL_VALUE',
            'DC3STEAMSO.MOVE',
            'DC3STEAMSO.BASE_CASE'
        ]})

    with pytest.raises(ValueError, match=r'No recognized properties present in "query" argument.'):
        spy.search(query_df, workbook=spy.GLOBALS_ONLY)

    with pytest.raises(ValueError, match=r'No recognized properties present in "query" argument.'):
        spy.search(dict(), workbook=spy.GLOBALS_ONLY)


@pytest.mark.system
def test_search_in_corporate_workbook():
    # Previously, other than specifying a workbook ID, there was no way to search in a workbook that is in the
    # corporate folder (or any other root directories than My Folder).
    workbook_name = f'test_sections_{_common.new_placeholder_guid()}'
    workbook = Analysis(workbook_name)
    workbook.worksheet('The Worksheet')
    spy.workbooks.push(workbook, path=f'{spy.workbooks.CORPORATE} >> test_search_in_corporate_workbook')

    # Search for the workbook by specifying the Corporate directory in the path
    wb_search_df = spy.workbooks.search({'Name': workbook_name,
                                         'Path': f'{spy.workbooks.CORPORATE} >> test_search_in_corporate_workbook'})

    wb_id = wb_search_df['ID'][0]

    # Check that the workbook ID in the corporate drive is correct
    assert wb_id == workbook.id

    # Push a signal to the workbook which is under corporate drive
    metadata = pd.DataFrame([{
        'Type': 'Scalar',
        'Name': 'Test Negative Number in a Corporate Drive Workbook',
        'Formula': np.int64(-12)
    }])

    spy.push(metadata=metadata, workbook=wb_id, worksheet=None)

    # Perform a spy.search in the corporate drive
    search_df = spy.search({
        'Name': 'Test Negative Number in a Corporate Drive Workbook',
    }, workbook=f'{spy.workbooks.CORPORATE} >> test_search_in_corporate_workbook >> {workbook_name}')

    # Check that spy.search() in the corporate drive found the signal
    assert len(search_df) > 0
    _assert_result(search_df, 'Success')
