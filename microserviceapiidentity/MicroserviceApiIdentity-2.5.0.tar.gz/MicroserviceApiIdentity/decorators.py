"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
from functools import wraps
import json
import jsonschema
import jwt
from flask import request, current_app, g
from MicroserviceApiIdentity.db import redis
from MicroserviceApiIdentity.response_builder import ResponseBuilder
from MicroserviceApiIdentity.dicts import ResponseStatusDict


def required_jwt_token(func):
    """Check JWT.
    """
    @wraps(func)
    def decorated_function(*args, **kwargs):
        jwt_token = request.headers.get('Authorization')
        jwt_secret = current_app.config['JWT_SECRET']
        jwt_alg = current_app.config['JWT_ALGORITHM']

        try:
            jwt_data = jwt.decode(jwt_token, jwt_secret, algorithm=jwt_alg)
        except Exception as error:
            current_app.logger.error(error)
            return ResponseBuilder(None, ResponseStatusDict.InvalidToken).get_response()
        if not redis.get(jwt_data['token']):
            return ResponseBuilder(None, ResponseStatusDict.ExpiredToken).get_response()

        g.token = jwt_data['token']
        g.account = json.loads(redis.get(g.token).decode())
        expire = 3600
        redis.expire(g.token, expire)

        return func(*args, **kwargs)
    return decorated_function


def required_jwt_token_with_priv(priv=None):
    def validation(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            jwt_token = request.headers.get('Authorization')
            jwt_secret = current_app.config['JWT_SECRET']
            jwt_alg = current_app.config['JWT_ALGORITHM']

            try:
                jwt_data = jwt.decode(jwt_token, jwt_secret, algorithm=jwt_alg)
            except Exception as error:
                current_app.logger.error(error)
                return ResponseBuilder(None, ResponseStatusDict.InvalidToken).get_response()
            
            if not redis.get(jwt_data['token']):
                return ResponseBuilder(None, ResponseStatusDict.ExpiredToken).get_response()

            g.token = jwt_data['token']
            g.account = json.loads(redis.get(g.token).decode())
            expire = 3600
            redis.expire(g.token, expire)

            return func(*args, **kwargs)
        return decorated_function
    return validation


def required_schema(schema):
    """Декоратор проверки схемы JSON

    :param schema: dict
    :return:

    >>> @required_schema({})
    """
    def validation(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            # check content type
            if not request.headers.get('content-type') == 'application/json':
                return ResponseBuilder(None, ResponseStatusDict.InvalidContentType).get_response()
            try:
                jsonschema.validate(request.json, schema)
            except jsonschema.exceptions.ValidationError as error:
                current_app.logger.error(error)
                return ResponseBuilder(None, ResponseStatusDict.InvalidContent).get_response()
            return func(*args, **kwargs)
        return decorated_function
    return validation
