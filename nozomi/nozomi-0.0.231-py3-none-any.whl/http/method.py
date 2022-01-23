"""
Nozomi
HTTPMethod Module
Copyright Amatino Pty Ltd
"""
from enum import Enum


class HTTPMethod(Enum):
    GET = 'GET'
    POST = 'POST'
    DELETE = 'DELETE'
    PUT = 'PUT'
    PATCH = 'PATCH'
