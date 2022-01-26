from functools import wraps
from flask import (
    request,
    abort
)
from werkzeug.exceptions import BadRequest
from werkzeug.routing import ValidationError


def validate_json(f):
    @wraps(f)
    def wrapper(*args, **kw):
        try:
            if request.get_json() is None:
                raise BadRequest
        except BadRequest:
            return abort(400, 'No JSON body')
        return f(*args, **kw)

    return wrapper


def validate(schema, json, path=''):
    for key in schema:
        req_type = schema[key]

        if isinstance(req_type, OptionalParam):
            if key not in json:
                continue
            req_type = req_type.get_type()

        if key not in json:
            raise ValidationError(f'Expected {path}{key} be defined!')

        if not isinstance(req_type, dict) and not isinstance(json[key], req_type):
            raise ValidationError(f'Expected {path}{key} to be {req_type.__name__}, was {type(json[key]).__name__}')

        if isinstance(req_type, dict) and not isinstance(json[key], dict):
            raise ValidationError(f'Expected {path}{key} to be dictionary, was {type(json[key]).__name__}')

        if isinstance(req_type, dict):
            validate(req_type, json[key], f'{key}.')
            continue

        # else:
        #  abort(500, f'Malformed server schema - {key}')


def validate_schema(schema):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kw):
            try:
                validate(schema, request.json)
            except ValidationError as e:
                return abort(400, str(e) if e else 'Invalid or malformed JSON')
            return f(*args, **kw)

        return wrapper

    return decorator


class OptionalParam:
    def __init__(self, t):
        self._type = t

    def get_type(self):
        return self._type
