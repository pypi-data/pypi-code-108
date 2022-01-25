import pandas as pd
import pytest

from seeq import spy
from seeq.spy.tests import test_common


def setup_module():
    test_common.initialize_sessions()


@pytest.mark.system
def test_plot():
    results = spy.search({
        "Path": "Example >> Cooling Tower 1 >> Area A"
    }, workbook=spy.GLOBALS_ONLY)

    my_signals = results.loc[results['Name'].isin(['Compressor Power', 'Temperature', 'Relative Humidity'])]

    calculated_data = spy.pull(
        my_signals,
        start='2019-01-01',
        end='2019-01-07',
        calculation='$signal.lowPassFilter(200min, 3min, 333)',
        grid='5min',
        header='Name')

    push_results = spy.push(metadata=pd.DataFrame([{
        'Name': 'Compressor on High',
        'Type': 'Condition',
        'Formula': '$cp.valueSearch(isGreaterThan(25kW))',
        'Formula Parameters': {
            # Note here that we are just using a row from our search results. The SPy module will figure
            # out that it contains an identifier that we can use.
            '$cp': results[results['Name'] == 'Compressor Power']
        }
    }]), workbook='test_plot', worksheet=None)

    capsules = spy.pull(push_results, start='2019-01-01', end='2019-01-07')

    samples = calculated_data

    spy.plot(samples=samples, capsules=capsules, show=False)

    # We aren't asserting anything here, just making sure we can execute the code without an exception.
