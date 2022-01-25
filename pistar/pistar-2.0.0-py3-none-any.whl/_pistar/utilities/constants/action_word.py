"""
description: this module provides two constants: ACTION_WORD_KEYS and
             ACTION_WORD_STATUS.

"""


class ACTION_WORD_KEYS:
    """
    description: the keys of action word document.
    """

    DESCRIPTION = 'description'
    ARGUMENTS = 'arguments'
    RETURN = 'return'
    AUTHOR = 'author'
    MODIFY_RECORDS = 'modify_records'
    STATUS = 'status'
    TAGS = 'tags'

    ASSERTION = 'assertion'
    ENUMERATION = 'enumeration'
    TYPE = 'type'
    ALLOW_NONE = 'allow_none'
    PROPERTIES = 'properties'
    REQUIRED = 'required'
    ITEMS = 'items'

    FIRST_ARGUMENT = 'sut'


class ACTION_WORD_STATUS:
    """
    description: the status of action word.
    """

    ENABLE = 'enable'
    DISABLE = 'disable'
    DEPRECATED = 'deprecate'
