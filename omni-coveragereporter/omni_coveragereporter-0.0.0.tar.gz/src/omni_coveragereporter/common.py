def valid(file_name):
    return not file_name.endswith('__init__.py') and 'test_' not in file_name
