import json

import numpy as np
import pandas as pd
import pytest

from seeq import spy
from seeq.sdk import *
from seeq.sdk.rest import ApiException
from seeq.spy import _common
from seeq.spy import _metadata
from seeq.spy.tests import test_common


def setup_module():
    test_common.initialize_sessions()


def assert_datasource_properties(datasource_output, name, datasource_class, datasource_id,
                                 expected_additional_properties):
    assert datasource_output.datasource_class == datasource_class
    assert datasource_output.datasource_id == datasource_id
    assert datasource_output.name == name
    assert not datasource_output.is_archived
    assert datasource_output.stored_in_seeq
    assert not datasource_output.cache_enabled
    assert datasource_output.description == _common.DEFAULT_DATASOURCE_DESCRIPTION
    assert len(datasource_output.additional_properties) == expected_additional_properties
    filtered_properties = filter(lambda x: x.name == 'Expect Duplicates During Indexing',
                                 datasource_output.additional_properties)
    additional_property = list(filtered_properties)[0]
    assert additional_property.value


@pytest.mark.system
def test_create_datasource():
    datasources_api = DatasourcesApi(spy.session.client)

    with pytest.raises(ValueError):
        _metadata.create_datasource(spy.session, 1)

    _metadata.create_datasource(spy.session, 'test_datasource_name_1')

    datasource_output_list = datasources_api.get_datasources(limit=100000)  # type: DatasourceOutputListV1
    datasource_output = list(filter(lambda d: d.name == 'test_datasource_name_1',
                                    datasource_output_list.datasources))[0]  # type: DatasourceOutputV1

    assert_datasource_properties(datasource_output,
                                 'test_datasource_name_1',
                                 _common.DEFAULT_DATASOURCE_CLASS,
                                 'test_datasource_name_1', 3)

    with pytest.raises(ValueError, match='"Datasource Name" required for datasource'):
        _metadata.create_datasource(spy.session, {
            'Blah': 'test_datasource_name_2'
        })

    datasource_output = _metadata.create_datasource(spy.session, {
        'Datasource Name': 'test_datasource_name_2'
    })
    assert_datasource_properties(datasource_output,
                                 'test_datasource_name_2',
                                 _common.DEFAULT_DATASOURCE_CLASS,
                                 'test_datasource_name_2', 3)

    datasource_output = _metadata.create_datasource(spy.session, {
        'Datasource Name': 'test_datasource_name_3',
        'Datasource ID': 'test_datasource_id_3'
    })
    assert_datasource_properties(datasource_output,
                                 'test_datasource_name_3',
                                 _common.DEFAULT_DATASOURCE_CLASS,
                                 'test_datasource_id_3', 3)

    with pytest.raises(ValueError):
        _metadata.create_datasource(spy.session, {
            'Datasource Class': 'test_datasource_class_4',
            'Datasource Name': 'test_datasource_name_4',
            'Datasource ID': 'test_datasource_id_4'
        })


@pytest.mark.system
def test_crab_25450():
    # This was a nasty bug. In the case where the user had a "Scoped To" column in their metadata DataFrame [possibly
    # as a result of creating it via spy.search(all_properties=True)], then _metadata.get_scoped_data_id() would
    # assign all items to global scope. The top of the asset tree would be locally scoped because it's treated
    # differently in _metadata._reify_path().
    #
    # _metadata.get_scoped_data_id() has been fixed so that it always sets a scope that is consistent with the Data
    # ID it is constructing. However, plenty of metadata has been pushed with the old bug in place, and we don't want
    # to cause a big headache of 'Attempted to set scope on a globally scoped item' errors coming back from Appserver
    # (read CRAB-25450 for more info).
    #
    # This test recreates the problem and then ensures the problem is handled by the code that detects the situation and
    # accommodates existing trees that have the problem.
    search_df = spy.search({'Name': 'Area E_Temperature'},
                           workbook=spy.GLOBALS_ONLY)

    # The to reproducing the problem is including a 'Scoped To' column that is blank
    metadata_df = pd.DataFrame([
        {
            'Name': 'test_CRAB_25450 Asset',
            'Type': 'Asset',
            'Path': 'test_CRAB_25450',
            'Asset': 'test_CRAB_25450 Asset',
            'Scoped To': np.nan
        },
        {
            'Name': 'test_CRAB_25450 Signal',
            'Type': 'Signal',
            'Formula': 'sinusoid()',
            'Path': 'test_CRAB_25450',
            'Asset': 'test_CRAB_25450 Asset',
            'Scoped To': np.nan
        },
        {
            'Name': 'test_CRAB_25450 Condition',
            'Type': 'Condition',
            'Formula': 'weeks()',
            'Path': 'test_CRAB_25450',
            'Asset': 'test_CRAB_25450 Asset',
            'Scoped To': np.nan
        },
        {
            'Name': 'test_CRAB_25450 Scalar',
            'Type': 'Scalar',
            'Formula': '1',
            'Path': 'test_CRAB_25450',
            'Asset': 'test_CRAB_25450 Asset',
            'Scoped To': np.nan
        },
        {
            'Type': 'Threshold Metric',
            'Name': 'push test threshold metric',
            'Measured Item': search_df.iloc[0]['ID'],
        }
    ])
    workbook = 'test_crab_25450'
    push_df = spy.push(metadata=metadata_df, workbook=workbook, worksheet=None, datasource=workbook)

    assert len(push_df) == 5

    items_api = ItemsApi(spy.client)
    assets_api = AssetsApi(spy.client)
    signals_api = SignalsApi(spy.client)
    conditions_api = ConditionsApi(spy.client)
    scalars_api = ScalarsApi(spy.client)
    metrics_api = MetricsApi(spy.client)

    for index, row in push_df.iterrows():
        # This recreates the bug by manually setting all the pushed items to global scope
        items_api.set_scope(id=row['ID'])

    def _get_outputs(_df):
        return (assets_api.get_asset(id=_df.iloc[0]['ID']),
                signals_api.get_signal(id=_df.iloc[1]['ID']),
                conditions_api.get_condition(id=_df.iloc[2]['ID']),
                scalars_api.get_scalar(id=_df.iloc[3]['ID']),
                metrics_api.get_metric(id=_df.iloc[4]['ID']))

    outputs = _get_outputs(push_df)

    for output in outputs:
        assert output.scoped_to is None

    # This will succeed due to our code to handle the situation.
    push2_df = spy.push(metadata=metadata_df, workbook=workbook, worksheet=None, datasource=workbook)

    for i in range(0, 5):
        assert push_df.iloc[i]['ID'] == push2_df.iloc[i]['ID']

    outputs = _get_outputs(push2_df)

    # The scope will still be wrong, but there's nothing we can do about it
    for output in outputs:
        assert output.scoped_to is None

    # Now push to a different workbook (without the recreation flag enabled)
    push3_df = spy.push(metadata=metadata_df, workbook=f'{workbook} - Corrected', worksheet=None, datasource=workbook)

    # Should be different items
    for i in range(0, 5):
        assert push_df.iloc[i]['ID'] != push3_df.iloc[i]['ID']

    outputs = _get_outputs(push3_df)

    # The scope will be correct
    for output in outputs:
        assert output.scoped_to is not None


# This can be enabled when CRAB-25580 is fixed
@pytest.mark.disabled
def test_bad_formula_error_message():
    search_df = spy.search({'Name': 'Area B_Temperature'},
                           workbook=spy.GLOBALS_ONLY)
    temperature_id = search_df.iloc[0]['ID']

    search_df = spy.search({'Name': 'Area B_Compressor Power'},
                           workbook=spy.GLOBALS_ONLY)
    power_id = search_df.iloc[0]['ID']

    conditions_api = ConditionsApi(spy.session.client)

    condition_input = ConditionInputV1(
        name='test_bad_formula',
        formula='$power > 20 kW and $temp < 60 Faq',
        parameters=[
            f'power={power_id}',
            f'temp={temperature_id}'
        ],
        datasource_id=_common.DEFAULT_DATASOURCE_ID,
        datasource_class=_common.DEFAULT_DATASOURCE_CLASS
    )

    expected_error = 'Unknown unit of measure \'Faq\' at \'Faq\', line=1, column=31'
    error_message = None
    try:
        conditions_api.create_condition(body=condition_input)
    except ApiException as e:
        error_message = json.loads(e.body)['statusMessage']

    assert expected_error in error_message

    item_batch_output = conditions_api.put_conditions(body=ConditionBatchInputV1(
        conditions=[condition_input]
    ))

    error_message = item_batch_output.item_updates[0].error_message

    assert expected_error in error_message
