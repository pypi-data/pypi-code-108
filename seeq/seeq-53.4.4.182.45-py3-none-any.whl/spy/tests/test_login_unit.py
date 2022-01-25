import json
import types

import pandas as pd
import pytest

from seeq import spy
from seeq.spy import _login


@pytest.mark.unit
def test_validate_seeq_server_version():
    module_major, module_minor, module_patch, module_functional = _login.get_module_version_tuple()

    spy.options.allow_version_mismatch = True

    status = spy.Status()
    spy.session.server_version = 'R22.0.36.01-v202007160902-SNAPSHOT'
    seeq_server_major, seeq_server_minor, seeq_server_patch = _login.validate_seeq_server_version(spy.session, status)
    assert len(status.warnings) == 1
    assert 'The major/minor version' in status.warnings.pop()
    assert (seeq_server_major, seeq_server_minor, seeq_server_patch) == (0, 36, 1)

    status = spy.Status()
    spy.session.server_version = 'R5000000.21.06-v203008100902-BETA'
    seeq_server_major, seeq_server_minor, seeq_server_patch = _login.validate_seeq_server_version(spy.session, status)
    assert len(status.warnings) == 1
    assert 'The major version' in status.warnings.pop()
    assert (seeq_server_major, seeq_server_minor, seeq_server_patch) == (5000000, 21, 6)

    status = spy.Status()
    spy.session.server_version = f'R{module_major}.{module_minor}.{module_patch}'
    seeq_server_major, seeq_server_minor, seeq_server_patch = _login.validate_seeq_server_version(spy.session, status)
    assert len(status.warnings) == 0
    assert (seeq_server_major, seeq_server_minor, seeq_server_patch) == (module_major, module_minor, module_patch)

    spy.options.allow_version_mismatch = False

    status = spy.Status()
    spy.session.server_version = 'R22.0.36.01-v202007160902-SNAPSHOT'
    with pytest.raises(RuntimeError, match=r'The major/minor version'):
        _login.validate_seeq_server_version(spy.session, status)


@pytest.mark.unit
def test_validate_start_and_end():
    # Save off the user from login so we can restore it at the end
    original_user = spy.session.user

    def _assert_with_margin(actual, expected):
        margin_in_seconds = 5 * 60
        actual_start, actual_end = actual
        expected_start = pd.to_datetime(expected[0])
        expected_end = pd.to_datetime(expected[1])
        assert abs(pd.Timedelta(actual_start - expected_start).total_seconds()) < margin_in_seconds
        assert abs(pd.Timedelta(actual_end - expected_end).total_seconds()) < margin_in_seconds
        assert actual_start.tz == expected_start.tz
        assert actual_end.tz == expected_end.tz

    try:
        utc_now = pd.Timestamp.now(tz='UTC')
        utc_yesterday = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=1)
        eastern_now = pd.Timestamp.now(tz='UTC').tz_convert('US/Eastern')
        eastern_yesterday = pd.Timestamp.now(tz='UTC').tz_convert(
            'US/Eastern') - pd.Timedelta(days=1)
        naive_yesterday = pd.Timestamp.utcnow().tz_localize(None) - pd.Timedelta(days=1)

        spy.session.user = None

        _assert_with_margin(
            _login.validate_start_and_end(spy.session, None, None), (utc_now - pd.Timedelta(hours=1), utc_now))

        _assert_with_margin(
            _login.validate_start_and_end(spy.session, utc_yesterday, None), (utc_yesterday, utc_now))

        _assert_with_margin(
            _login.validate_start_and_end(spy.session, None, utc_yesterday),
            (utc_yesterday - pd.Timedelta(hours=1), utc_yesterday))

        _assert_with_margin(
            _login.validate_start_and_end(spy.session, eastern_yesterday, None), (eastern_yesterday, eastern_now))

        _assert_with_margin(
            _login.validate_start_and_end(spy.session, None, eastern_yesterday),
            (eastern_yesterday - pd.Timedelta(hours=1), eastern_yesterday))

        _assert_with_margin(
            _login.validate_start_and_end(spy.session, naive_yesterday, None), (utc_yesterday, utc_now))

        _assert_with_margin(
            _login.validate_start_and_end(spy.session, None, naive_yesterday),
            (utc_yesterday - pd.Timedelta(hours=1), utc_yesterday))

        spy.session.user = types.SimpleNamespace(workbench=json.dumps({
            'state': {'stores': {'sqWorkbenchStore': {'userTimeZone': 'US/Eastern'}}}
        }))

        _assert_with_margin(_login.validate_start_and_end(
            spy.session,
            # Make timestamps timezone-naive
            eastern_yesterday.tz_localize(None), None),
            (eastern_yesterday, eastern_now))

        _assert_with_margin(_login.validate_start_and_end(
            spy.session,
            # Make timestamps timezone-naive
            None, eastern_yesterday.tz_localize(None)),
            (eastern_yesterday - pd.Timedelta(hours=1), eastern_yesterday))

    finally:
        spy.session.user = original_user
