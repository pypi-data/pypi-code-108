"""Tests for log sub-commands"""

# 3rd party imports
import pytest
from freezegun import freeze_time
from colorama import Fore, Style


@freeze_time("2021-12-30")
def test_no_args_opens_today(dispatcher, ntbk_dir):
    """Test calling app without any args opens todays file"""
    expected_path = ntbk_dir / 'log/2021/12-december/2021-12-30/index.md'
    dispatcher.run([])
    dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_path)
    assert expected_path.parent.exists()

@freeze_time("2021-12-30")
def test_today_default_file(dispatcher, ntbk_dir):
    """Test 'today' arg opens todays file"""
    aliases = ['today', 'tod']
    expected_path = ntbk_dir / 'log/2021/12-december/2021-12-30/index.md'
    for alias in aliases:
        dispatcher.run([alias])
        dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_path)
        dispatcher.filesystem.open_file_in_editor.reset_mock()
    assert expected_path.parent.exists()


@freeze_time("2021-01-01")
def test_today_other_file(dispatcher, ntbk_dir):
    """Test specifying a different file for 'today' command"""
    aliases = ['today', 'tod']
    expected_path = ntbk_dir / 'log/2021/01-january/2021-01-01/test.md'
    for alias in aliases:
        dispatcher.run([alias, 'test'])
        dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_path)
        dispatcher.filesystem.open_file_in_editor.reset_mock()
    assert expected_path.parent.exists()

@freeze_time("2021-07-20")
def test_yesterday_default_file(dispatcher, ntbk_dir):
    """Test 'yesterday' arg opens yesterday's file"""
    aliases = ['yesterday', 'yest']
    expected_path = ntbk_dir / 'log/2021/07-july/2021-07-19/index.md'
    for alias in aliases:
        dispatcher.run([alias])
        dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_path)
        dispatcher.filesystem.open_file_in_editor.reset_mock()
    assert expected_path.parent.exists()

@freeze_time("2021-07-20")
def test_yesterday_other_file(dispatcher, ntbk_dir):
    """Test specifying a different file for 'yesterday' command"""
    aliases = ['yesterday', 'yest']
    expected_path = ntbk_dir / 'log/2021/07-july/2021-07-19/work.md'
    for alias in aliases:
        dispatcher.run([alias, 'work'])
        dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_path)
        dispatcher.filesystem.open_file_in_editor.reset_mock()
    assert expected_path.parent.exists()

@freeze_time("2020-02-15")
def test_tomorrow_default_file(dispatcher, ntbk_dir):
    """Test 'tomorrow' arg opens tomorrow's file"""
    aliases = ['tomorrow', 'tom']
    expected_path = ntbk_dir / 'log/2020/02-february/2020-02-16/index.md'
    for alias in aliases:
        dispatcher.run([alias])
        dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_path)
        dispatcher.filesystem.open_file_in_editor.reset_mock()
    assert expected_path.parent.exists()

@freeze_time("2020-02-15")
def test_tomorrow_other_file(dispatcher, ntbk_dir):
    """Test specifying a different file for 'tomorrow' command"""
    aliases = ['tomorrow', 'tom']
    expected_path = ntbk_dir / 'log/2020/02-february/2020-02-16/notes.md'
    for alias in aliases:
        dispatcher.run([alias, 'notes'])
        dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_path)
        dispatcher.filesystem.open_file_in_editor.reset_mock()
    assert expected_path.parent.exists()

@freeze_time("2021-01-01")
def test_date_default_file(dispatcher, ntbk_dir):
    """Test 'date' arg opens specified date's index file"""
    aliases = ['date', 'dt', 'd']
    expected_path = ntbk_dir / 'log/2020/03-march/2020-03-01/index.md'
    for alias in aliases:
        dispatcher.run([alias, '2020-03-01'])
        dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_path)
        dispatcher.filesystem.open_file_in_editor.reset_mock()
    assert expected_path.parent.exists()

@freeze_time("2021-01-01")
def test_date_other_file(dispatcher, ntbk_dir):
    """Test specifying a different file for 'date' command"""
    aliases = ['date', 'dt', 'd']
    expected_path = ntbk_dir / 'log/2021/03-march/2021-03-01/notes.md'
    for alias in aliases:
        dispatcher.run([alias, '2021-03-01', 'notes'])
        dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_path)
        dispatcher.filesystem.open_file_in_editor.reset_mock()
    assert expected_path.parent.exists()

def test_non_iso_date_fails(dispatcher):
    """Test that date command requires date to be iso format"""
    with pytest.raises(SystemExit):
        dispatcher.run(['date', '01/01/2020'])
    dispatcher.filesystem.open_file_in_editor.assert_not_called()

@freeze_time("2021-01-01")
def test_finding_log_index_file(dispatcher, ntbk_dir, mocker):
    """Test using --find flag outputs path to the default log file"""
    mocker.patch('builtins.print')
    expected_path = ntbk_dir / 'log/2021/01-january/2021-01-01/index.md'
    dispatcher.run(['today', '--find'])
    print.assert_called_once_with(expected_path)

def test_finding_log_other_file(dispatcher, ntbk_dir, mocker):
    """Test using --find flag outputs path to the specified log file"""
    mocker.patch('builtins.print')
    expected_path = ntbk_dir / 'log/2021/01-january/2021-01-01/notes.md'
    dispatcher.run(['date', '2021-01-01', 'notes', '--find'])
    print.assert_called_once_with(expected_path)

@freeze_time("2021-01-01")
def test_finding_logdate(dispatcher, ntbk_dir, mocker):
    """Test using --find-dir flag outputs path to specified date"""
    mocker.patch('builtins.print')
    expected_path = ntbk_dir / 'log/2021/01-january/2021-01-01'
    dispatcher.run(['today', '--find-dir'])
    print.assert_called_once_with(expected_path)

@freeze_time("2021-12-30")
def test_jot_default_file(dispatcher, ntbk_dir, mocker):
    """Test jotting note without any args to todays default file"""
    mocker.patch('builtins.print')
    expected_path = ntbk_dir / 'log/2021/12-december/2021-12-30/index.md'
    dispatcher.run(['jot', 'hello world'])
    assert expected_path.read_text() == '\n\nhello world'
    print.assert_called_once_with(f"{Fore.GREEN}Jotted note to today's index file{Style.RESET_ALL}")

@freeze_time("2021-12-30 10:15 AM")
def test_jot_default_file_timestamped(dispatcher, ntbk_dir, mocker):
    """Test jotting note without any args to todays default file"""
    mocker.patch('builtins.print')
    expected_path = ntbk_dir / 'log/2021/12-december/2021-12-30/index.md'
    dispatcher.run(['jot', 'hello world', '-s'])
    assert expected_path.read_text() == '\n\n[10:15 AM]\nhello world'
    print.assert_called_once_with(f"{Fore.GREEN}Jotted note to today's index file{Style.RESET_ALL}")

@freeze_time("2021-12-30")
def test_jot_other_file(dispatcher, ntbk_dir, mocker):
    """Test jotting note without any args to todays default file"""
    mocker.patch('builtins.print')
    expected_path = ntbk_dir / 'log/2021/12-december/2021-12-30/work.md'
    dispatcher.run(['jot', 'hello world', 'work'])
    assert expected_path.read_text() == '\n\nhello world'
    print.assert_called_once_with(f"{Fore.GREEN}Jotted note to today's work file{Style.RESET_ALL}")

@freeze_time("2021-12-30 10:15 AM")
def test_jot_other_file_timestamped(dispatcher, ntbk_dir, mocker):
    """Test jotting note without any args to todays default file"""
    mocker.patch('builtins.print')
    expected_path = ntbk_dir / 'log/2021/12-december/2021-12-30/work.md'
    dispatcher.run(['jot', 'hello world', 'work', '-s'])
    assert expected_path.read_text() == '\n\n[10:15 AM]\nhello world'
    print.assert_called_once_with(f"{Fore.GREEN}Jotted note to today's work file{Style.RESET_ALL}")
