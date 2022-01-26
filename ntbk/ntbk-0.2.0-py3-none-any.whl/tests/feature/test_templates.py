"""Test using templates with commands"""

from freezegun import freeze_time

@freeze_time('2021-01-01')
def test_creating_new_log_with_default_template(dispatcher, ntbk_dir, template_factory):
    """Test using a configured default template for a log file"""
    template = template_factory()
    dispatcher.config.set('default_templates', {'log': { 'index': template.get_name() }})
    expected_file = ntbk_dir / 'log/2021/01-january/2021-01-01/index.md'
    dispatcher.run(['today'])
    assert expected_file.read_text() == template.render()
    dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_file)

def test_creating_new_collection_with_default_template(dispatcher, ntbk_dir, template_factory):
    """Test using a configured default template for a collection file"""
    template = template_factory()
    dispatcher.config.set('default_templates', {'collection': { 'books': template.get_name() }})
    expected_file = ntbk_dir / 'collections/books/1984.md'
    dispatcher.run(['collection', 'books', '1984'])
    assert expected_file.read_text() == template.render()
    dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_file)

# Eventually I'd like to make it actually overwrite files that are empty
# (newlines and spaces wouldnt count as content)
def test_existing_file_not_overwritten(dispatcher, collection_file, template_factory):
    """Test if a template is specified but the file is not empty it is not overwritten"""
    template = template_factory()
    c_name = collection_file.get_collection().get_name()
    dispatcher.config.set('default_templates', {'collection': { c_name: template.get_name() }})
    collection_file.get_path().write_text('Placeholder text')
    dispatcher.run(['collection', c_name, collection_file.get_name()])
    # make sure the existing text is not overwritten by the default template
    assert collection_file.get_path().read_text() == 'Placeholder text'
    dispatcher.filesystem.open_file_in_editor.assert_called_with(collection_file.get_path())

@freeze_time('2021-01-01')
def test_creating_log_with_template_arg(dispatcher, ntbk_dir, template_factory):
    """Test creating a log file with the --template arg"""
    template = template_factory()
    expected_file = ntbk_dir / 'log/2021/01-january/2021-01-01/index.md'
    dispatcher.run(['today', '--template', template.get_name()])
    assert expected_file.read_text() == template.render()
    dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_file)

def test_creating_collection_with_template_arg(dispatcher, ntbk_dir, template_factory):
    """Test creating a collection file with the --template arg"""
    template = template_factory()
    expected_file = ntbk_dir / 'collections/books/1984.md'
    dispatcher.run(['collection', 'books', '1984', '--template', template.get_name()])
    assert expected_file.read_text() == template.render()
    dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_file)

@freeze_time('2021-01-01 03:21:34')
def test_standard_variables_replaced(dispatcher, ntbk_dir, template_factory):
    """Test that all default variables are replaced correctly in templates"""
    template_content = '{{ now.strftime("%A") }}\n'\
        '{{ today_iso }}\n'\
        '{{ now_iso }}\n'\
        '{{ today_long }}\n'\
        '{{ now_long }}\n'\
        '{{ log_date.strftime("%A") }}'
    template = template_factory(content=template_content)
    expected_file = ntbk_dir / 'log/2021/01-january/2021-01-01/index.md'
    dispatcher.run(['today', '--template', template.get_name()])
    assert expected_file.read_text() == 'Friday\n'\
        '2021-01-01\n'\
        '2021-01-01T03:21:34\n'\
        'Friday, January 01, 2021\n'\
        'Friday, January 01, 2021 03:21 AM\n'\
        'Friday'

@freeze_time('2021-01-01')
def test_config_template_variables(dispatcher, ntbk_dir, template_factory):
    """Test that all variables in config file get replaced in template file"""
    dispatcher.config.set('template_vars', { 'first_name': 'John', 'last_name': 'Doe'})
    template_content = '{{ first_name }} {{ last_name }}'
    template = template_factory(content=template_content)
    expected_file = ntbk_dir / 'log/2021/01-january/2021-01-01/index.md'
    dispatcher.run(['today', '--template', template.get_name()])
    assert expected_file.read_text() == 'John Doe'

def test_var_arg_variables(dispatcher, ntbk_dir, template_factory):
    """Test replacing variables provided with --vars flag"""
    template_content = '{{ title }} by {{ author }}'
    template = template_factory(content=template_content)
    expected_file = ntbk_dir / 'collections/books/dune.md'

    dispatcher.run(['collection', 'books', 'dune',
        '--template', template.get_name(), '--vars', 'title=Dune', 'author=Frank Herbert'])

    assert expected_file.read_text() == 'Dune by Frank Herbert'

@freeze_time('2021-12-25')
def test_template_with_all_vars(dispatcher, ntbk_dir, template_factory):
    """Test template with variables from default, config, and --vars"""
    template_content = '# Review of {{ title }} by {{ author }}\n'\
        'Written by {{ notebook_owner }} on {{ today_iso }}'
    dispatcher.config.set('template_vars', { 'notebook_owner': 'John Doe' })
    template = template_factory(content=template_content)
    expected_file = ntbk_dir / 'collections/book-reviews/dune.md'

    dispatcher.run(['collection', 'book-reviews', 'dune',
        '--template', template.get_name(), '--vars', 'title=Dune', 'author=Frank Herbert'])

    assert expected_file.read_text() == '# Review of Dune by Frank Herbert\n'\
        'Written by John Doe on 2021-12-25'

@freeze_time('2021-01-01')
def test_template_that_doesnt_exist(dispatcher, ntbk_dir, mocker):
    """Test creating a log file with the --template arg"""
    mocker.patch('builtins.print')
    expected_file = ntbk_dir / 'log/2021/01-january/2021-01-01/index.md'
    dispatcher.run(['today', '--template', 'does-not-exist'])
    print.assert_called_once_with('Template "does-not-exist" not found.')
    dispatcher.filesystem.open_file_in_editor.assert_called_with(expected_file)
    assert expected_file.read_text() == ''
