"""
description: this module provides three constants: API_DOCUMENT_FIELD,
             API_ARGUMENT_FIELD, and FROM.
"""


class API_DOCUMENT_FIELD:
    """
    description: the field names of api document.
    """

    DESCRIPTION = 'description'
    SUMMARY = 'summary'
    ARGUMENTS = 'arguments'
    RESPONSE = 'response'
    API_PATH = 'api_path'
    METHODS = 'methods'
    STATUS = 'status'


class API_ARGUMENT_FIELD:
    """
    description: the field names of argument document.
    """

    FROM = 'from'
    TYPE = 'type'
    DESCRIPTION = 'description'
    EXAMPLE = 'example'
    ASSERTION = 'assertion'
    ENUMERATION = 'enumeration'
    REQUIRED = 'required'
    DEFAULT = 'default'


class FROM:
    """
    description: the places contains the parameters.
    """

    QUERY = 'query'
    PATH = 'path'
    BODY = 'body'
    ENTIRE_BODY = 'entire_body'
    HEADER = 'header'
