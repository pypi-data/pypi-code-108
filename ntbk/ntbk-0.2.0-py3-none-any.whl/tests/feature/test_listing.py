"""Test listing templates, collections, and files"""
from unittest.mock import call
from colorama import Fore, Style
from freezegun import freeze_time

def test_listing_templates(dispatcher, filesystem, mocker):
    """Test 'templates' command lists all templates"""
    mocker.patch('builtins.print')
    template_path = filesystem.get_templates_base_path()
    template_path.mkdir(parents=True)
    (template_path / 'template_one.md').touch()
    (template_path / 'template_two.md').touch()

    dispatcher.run(['templates'])

    # With any_order=False we make sure they are printed in this order too
    print.assert_has_calls([call('template_one'), call('template_two')], any_order=False)

def test_listing_collections(dispatcher, filesystem, mocker):
    """Test 'collections' command lists all collections"""
    aliases = ['collections', 'cols']
    mocker.patch('builtins.print')
    col_path = filesystem.get_collection_base_path()
    (col_path / 'books').mkdir(parents=True)
    (col_path / 'books' / 'index.md').touch()
    (col_path / 'recipes').mkdir(parents=True)
    (col_path / 'recipes' / 'chili.md').touch()
    (col_path / 'recipes' / 'lasagna.md').touch()

    for alias in aliases:
        dispatcher.run([alias])

        # With any_order=False we make sure they are printed in this order too
        print.assert_has_calls([
            call('books'),
            call('recipes')],
            any_order=False)

        print.reset_mock()

@freeze_time("2020-01-01")
def test_listing_log_files_for_day(dispatcher, filesystem, mocker):
    """Test --list flag on log lists all files"""
    mocker.patch('builtins.print')
    log_base = filesystem.get_log_base_path()
    day_path = log_base / '2020/01-january/2020-01-01'
    day_path.mkdir(parents=True)
    (day_path / 'index.md').touch()
    (day_path / 'work.md').touch()
    (day_path / 'subdir').mkdir()
    (day_path / 'subdir' / 'index.md').touch() # this will be ignored

    dispatcher.run(['today', '--list'])

    # With any_order=False we make sure they are printed in this order too
    print.assert_has_calls([
        call('index'),
        call(Fore.BLUE + 'subdir/' + Style.RESET_ALL),
        call('work')],
        any_order=False)

def test_listing_collection_files(dispatcher, filesystem, mocker):
    """test --list flag on collection lists all collection files"""
    mocker.patch('builtins.print')
    col_base = filesystem.get_collection_base_path()
    col_path = col_base / 'travel'
    col_path.mkdir(parents=True)
    (col_path / 'montana.md').touch()
    (col_path / 'utah.md').touch()
    (col_path / 'alaska.md').touch()
    (col_path / 'wyoming').mkdir()
    (col_path / 'wyoming' / 'laramie.md').touch() # this will be ignored

    dispatcher.run(['collection', 'travel', '--list'])

    # With any_order=False we make sure they are printed in this order too
    print.assert_has_calls([
        call('alaska'),
        call('montana'),
        call('utah'),
        call(Fore.BLUE + 'wyoming/' + Style.RESET_ALL)],
        any_order=False)

def test_listing_collection_subdir_files(dispatcher, filesystem, mocker):
    """test --list flag on a nested collection lists all files"""
    mocker.patch('builtins.print')
    col_base = filesystem.get_collection_base_path()
    col_path = col_base / 'travel'
    col_path.mkdir(parents=True)
    (col_path / 'montana.md').touch() # should be ignored
    (col_path / 'alaska.md').touch() # should be ignored
    (col_path / 'wyoming').mkdir()
    (col_path / 'wyoming' / 'index.md').touch()
    (col_path / 'wyoming' / 'laramie').mkdir()

    dispatcher.run(['collection', 'travel/wyoming', '--list'])

    # With any_order=False we make sure they are printed in this order too
    print.assert_has_calls([
        call('index'),
        call(Fore.BLUE + 'laramie/' + Style.RESET_ALL)],
        any_order=False)

@freeze_time("2020-01-01")
def test_listing_log_subdir_files_for_day(dispatcher, filesystem, mocker):
    """Test --list flag on log lists all files"""
    mocker.patch('builtins.print')
    log_base = filesystem.get_log_base_path()
    day_path = log_base / '2020/01-january/2020-01-01'
    day_path.mkdir(parents=True)
    (day_path / 'index.md').touch() # this will be ignored
    (day_path / 'journal').mkdir()
    (day_path / 'journal' / 'morning.md').touch()
    (day_path / 'journal' / 'evening.md').touch()

    # For LogDate the path is in the file, but must end with a slash
    dispatcher.run(['today', 'journal/', '--list'])

    # With any_order=False we make sure they are printed in this order too
    print.assert_has_calls([
        call('evening'),
        call('morning')],
        any_order=False)

def test_listing_collection_subdir_files_recursive(dispatcher, filesystem, mocker):
    """test -lr flag on a nested collection lists all files"""
    mocker.patch('builtins.print')
    col_base = filesystem.get_collection_base_path()
    col_path = col_base / 'travel'
    col_path.mkdir(parents=True)
    (col_path / 'montana.md').touch() # should be ignored
    (col_path / 'alaska.md').touch() # should be ignored
    (col_path / 'wyoming').mkdir()
    (col_path / 'wyoming' / 'index.md').touch()
    (col_path / 'wyoming' / 'laramie').mkdir()
    (col_path / 'wyoming' / 'laramie' / 'restaurants.md').touch()

    dispatcher.run(['collection', 'travel', '-lr'])

    # With any_order=False we make sure they are printed in this order too
    print.assert_has_calls([
        call('alaska'),
        call('montana'),
        call(Fore.BLUE + 'wyoming/' + Style.RESET_ALL),
        call('wyoming/index'),
        call(Fore.BLUE + 'wyoming/laramie/' + Style.RESET_ALL),
        call('wyoming/laramie/restaurants')],
        any_order=False)

@freeze_time("2020-01-01")
def test_listing_log_files_for_day_recursive(dispatcher, filesystem, mocker):
    """Test -lr flag on log lists all files"""
    mocker.patch('builtins.print')
    log_base = filesystem.get_log_base_path()
    day_path = log_base / '2020/01-january/2020-01-01'
    day_path.mkdir(parents=True)
    (day_path / 'index.md').touch()
    (day_path / 'journal').mkdir()
    (day_path / 'journal' / 'morning.md').touch()
    (day_path / 'journal' / 'evening.md').touch()

    # For LogDate the path is in the file, but must end with a slash
    dispatcher.run(['today', '-lr'])

    # With any_order=False we make sure they are printed in this order too
    print.assert_has_calls([
        call('index'),
        call(Fore.BLUE + 'journal/' + Style.RESET_ALL),
        call('journal/evening'),
        call('journal/morning')],
        any_order=False)

@freeze_time("2020-01-01")
def test_listing_log_subdir_recursive(dispatcher, filesystem, mocker):
    """Test -lr flag on log subdirectory lists all files in that subdir"""
    mocker.patch('builtins.print')
    log_base = filesystem.get_log_base_path()
    day_path = log_base / '2020/01-january/2020-01-01'
    day_path.mkdir(parents=True)
    (day_path / 'index.md').touch()
    (day_path / 'journal').mkdir()
    (day_path / 'journal' / 'morning.md').touch()
    (day_path / 'journal' / 'evening.md').touch()
    (day_path / 'journal' / 'afternoon').mkdir()
    (day_path / 'journal' / 'afternoon' / 'index.md').touch()

    # For LogDate the path is in the file, but must end with a slash
    dispatcher.run(['today', 'journal/', '-lr'])

    # With any_order=False we make sure they are printed in this order too
    print.assert_has_calls([
        call(Fore.BLUE + 'afternoon/' + Style.RESET_ALL),
        call('afternoon/index'),
        call('evening'),
        call('morning')],
        any_order=False)
