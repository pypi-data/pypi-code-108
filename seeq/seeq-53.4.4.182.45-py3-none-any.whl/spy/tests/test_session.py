import pandas as pd
import pytest

from seeq import spy
from seeq.sdk.configuration import ClientConfiguration
from seeq.sdk.rest import ApiException
from seeq.spy.tests import test_common
from seeq.spy.tests.test_common import Sessions


@pytest.mark.unit
def test_session_segregation():
    session1 = spy.Session()
    session2 = spy.Session()

    default_retry = ClientConfiguration.DEFAULT_RETRY_TIMEOUT_IN_SECONDS

    assert session1.options.retry_timeout_in_seconds == default_retry
    assert session2.options.retry_timeout_in_seconds == default_retry
    assert session1.client_configuration.verify_ssl
    assert session2.client_configuration.verify_ssl

    session1.client_configuration.verify_ssl = False
    session2.options.retry_timeout_in_seconds = 3254

    assert session1.client_configuration.retry_timeout_in_seconds == default_retry
    assert session2.client_configuration.retry_timeout_in_seconds == 3254
    assert not session1.client_configuration.verify_ssl
    assert session2.client_configuration.verify_ssl


@pytest.mark.system
def test_multiple_login_sessions():
    test_common.initialize_sessions()

    # Log out so that the default session cannot be incorrectly used for any API calls
    test_common.log_out_default_user()

    try:
        session_ren = test_common.get_session(Sessions.ren)
        session_stimpy = test_common.get_session(Sessions.stimpy)

        numeric_data_df = pd.DataFrame()
        numeric_data_df['Spumco Signal'] = \
            pd.Series([3, 4], index=[pd.to_datetime('2019-01-01T00:00:00Z'), pd.to_datetime('2019-01-03T00:00:00Z')])
        ren_push_df = spy.push(numeric_data_df, session=session_ren)

        numeric_data_df = pd.DataFrame()
        numeric_data_df['Spumco Signal'] = \
            pd.Series([4, 5], index=[pd.to_datetime('2019-01-02T00:00:00Z'), pd.to_datetime('2019-01-04T00:00:00Z')])
        stimpy_push_df = spy.push(numeric_data_df, session=session_stimpy)

        ren_search_df = spy.search({'Name': 'Spumco Signal'}, session=session_ren, all_properties=True)
        stimpy_search_df = spy.search({'Name': 'Spumco Signal'}, session=session_stimpy, all_properties=True)

        assert ren_search_df.iloc[0]['ID'] == ren_push_df.iloc[0]['ID']
        assert stimpy_search_df.iloc[0]['ID'] == stimpy_push_df.iloc[0]['ID']

        assert ren_search_df.iloc[0]['ID'] != stimpy_search_df.iloc[0]['ID']

        ren_pull_df = spy.pull(ren_search_df, start='2019-01-01T00:00:00Z', end='2019-01-04T00:00:00Z',
                               grid=None, session=session_ren)
        stimpy_pull_df = spy.pull(stimpy_search_df, start='2019-01-01T00:00:00Z', end='2019-01-04T00:00:00Z',
                                  grid=None, session=session_stimpy)

        assert len(ren_pull_df) == 2
        assert len(stimpy_pull_df) == 2
        assert ren_pull_df.index.tolist() == [pd.to_datetime('2019-01-01T00:00:00Z'),
                                              pd.to_datetime('2019-01-03T00:00:00Z')]
        assert stimpy_pull_df.index.tolist() == [pd.to_datetime('2019-01-02T00:00:00Z'),
                                                 pd.to_datetime('2019-01-04T00:00:00Z')]
        assert ren_pull_df['Spumco Signal'].tolist() == [3, 4]
        assert stimpy_pull_df['Spumco Signal'].tolist() == [4, 5]

        ren_workbooks = spy.workbooks.pull(ren_push_df.spy.workbook_url, session=session_ren)
        stimpy_workbooks = spy.workbooks.pull(stimpy_push_df.spy.workbook_url, session=session_stimpy)

        # Ren doesn't have access to Stimpy's workbook and vice-versa
        with pytest.raises(ApiException, match='does not have access'):
            spy.workbooks.pull(stimpy_push_df.spy.workbook_url, session=session_ren)

        with pytest.raises(ApiException, match='does not have access'):
            spy.workbooks.pull(ren_push_df.spy.workbook_url, session=session_stimpy)

        assert len(ren_workbooks) == 1
        assert len(stimpy_workbooks) == 1

        ren_workbook = ren_workbooks[0]
        stimpy_workbook = stimpy_workbooks[0]

        assert ren_workbook.worksheets[0].display_items.iloc[0]['ID'] == ren_push_df.iloc[0]['ID']
        assert stimpy_workbook.worksheets[0].display_items.iloc[0]['ID'] == stimpy_push_df.iloc[0]['ID']

    finally:
        test_common.log_in_default_user()
