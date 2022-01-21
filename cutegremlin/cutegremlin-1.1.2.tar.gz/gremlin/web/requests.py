#!/usr/bin/env python3
from typing import Dict
from uuid import UUID
import re


def createResponse(statusCode: int, body: Dict):
    """
        Creates a response object with a user provided status code and message.
    """
    return {
        # 'isBase64Encoded': True,
        'statusCode': statusCode,
        # 'headers': {},
        'body': body
    }


def createMessageResponse(statusCode: int, message: str):
    """
        Creates a response with a formatted error message.
    """
    return createResponse(statusCode, {
        'message': message
    })


def success(body: Dict):
    """
        Creates a response object with a
        '200' status code and a payload.
    """
    return createResponse(200, body)


def accepted(message: str):
    """
        Creates a response object with a
        '200' status code and the user's message.
    """
    return createMessageResponse(202, message)


def serverError(message: str):
    """
        Creates a response object with a
        '500' status code and the user's message.
    """
    return createMessageResponse(500, message)


def badRequest(message: str):
    """
        Creates a response object with a
        '400' status code and the user's message.
    """
    return createMessageResponse(400, message)


def forbidden(message: str):
    """
        Creates a response object with a
        '403' status code and the user's message.
    """
    return createMessageResponse(403, message)


def unauthorized(message: str):
    """
        Creates a response object with a
        '401' status code and the user's message.
    """
    return createMessageResponse(401, message)


def isValidUuid(string: str, version: int = 4) -> bool:
    """
    Check if string is a valid UUID.

    Args:
        string : str
        version : {1, 2, 3, 4}
    """
    try:
        string = string.lower()
        uuidObj = UUID(string, version=version)
    except ValueError:
        return False

    return str(uuidObj).lower() == string


def isUrl(string: str) -> bool:
    """
        Check if a string is a valid URL.
    """

    # https://stackoverflow.com/a/7160778/10167844
    regex = re.compile(
        r'^(?:(?:http|ftp)s?://|)'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+'
        r'(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return re.match(regex, string) is not None


def isIP(string: str) -> bool:
    """
        Check if a string is a valid IP address.
    """
    regex = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
    return re.match(regex, string) is not None
