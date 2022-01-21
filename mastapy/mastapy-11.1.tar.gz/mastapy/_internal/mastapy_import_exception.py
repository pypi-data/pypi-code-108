'''mastapy_import_exception.py

Module containing mastapy import exceptions.
'''


class MastapyImportException(Exception):
    '''Custom exception for errors on import.

    We can't use the ImportError class because that just gets swallowed.
    '''
