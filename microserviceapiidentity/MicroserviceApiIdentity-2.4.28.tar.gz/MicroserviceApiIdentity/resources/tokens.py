"""Copyright (C) 2015-2021 Stack Web Services LLC. All rights reserved."""
import json
from uuid import uuid4
import validators
import jwt
from flask import current_app, g, request
from flask_restful import Resource
from MicroserviceApiIdentity.models import UsersModel, AttrsModel
from MicroserviceApiIdentity.decorators import required_jwt_token, required_schema
from MicroserviceApiIdentity.db import redis, database
from MicroserviceApiIdentity.response_builder import ResponseBuilder
from MicroserviceApiIdentity.dicts import ResponseStatusDict


class TokensResource(Resource):
    """Token endpoint class"""
    @staticmethod
    def user_data_to_dict(data) -> dict:
        """Create user data dict

        >>> TokensResource.user_data_to_dict(data)
        {
            "id": "50854b9a-9582-4e5b-8df7-8d48dd95f6a7",
            "email": "test@test.ru"
        }
        """
        return {
            "id": str(data.id),
            "email": data.email,
        }

    @staticmethod
    def user_attrs_to_dict(user_id):
        attrs = database.session.query(
            AttrsModel.attr_name,
            AttrsModel.attr_type,
            AttrsModel.attr_value
        ).filter_by(
            user=str(user_id)
        ).all()

        result = dict()
        for attr in attrs:
            attr_value = attr.attr_value
            if attr.attr_type == "integer":
                attr_value = int(attr.attr_value)
            if attr.attr_type == "bool":
                attr_value = bool(attr.attr_value)
            result[attr.attr_name] = attr_value
        return result

    @required_schema({
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email"
            },
            "password": {
                "type": "string"
            },
            "use_cookie": {
                "type": "string"
            }
        },
        "required": [
            "email",
            "password"
        ]
    })
    def post(self):
        """Create new token

        curl -X POST 'http://localhost:5000/v2/tokens' \
        -H 'Content-Type: application/json' \
        -d '{"email": "vanzhiganov@ya.ru", "password": "..."}'

        curl -X POST 'http://localhost:5000/v2/tokens' \
        -H 'Content-Type: application/json' \
        -d '{"email": "vanzhiganov@ya.ru", "password": "...", "use_cookie": "yes"}'
        """
        email = request.json.get('email')
        password = request.json.get('password')

        # check valid email
        if not validators.email(email):
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0100).get_response()
        #
        if not UsersModel.auth(email, password, 1):
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0101).get_response()

        user = UsersModel.get_item_by_email(email)
        attrs = self.user_attrs_to_dict(user.id)

        expire = 86400
        token = str(uuid4())
        redis.set(token, json.dumps(self.user_data_to_dict(user)))
        redis.expire(token, expire)
        jwt_token = jwt.encode(
            {
                'token': token,
                'email': user.email,
                'user_id': str(user.id),
                'attrs': attrs
            },
            current_app.config['JWT_SECRET'],
            algorithm=current_app.config['JWT_ALGORITHM'],
        )

        #
        UsersModel.update_last_visit_time(user.id)

        response = ResponseBuilder(None, ResponseStatusDict.Created)

        if request.json.get('use_cookie'):
            response.set_cookie('/', jwt_token.decode())
        else:
            response.set_payload({"token": jwt_token.decode()})

        return response.get_response()

    @required_jwt_token
    def delete(self):
        """Revoke current token

        curl -X DELETE 'http://localhost:5000/v2/tokens' \
        -H 'X-Token: ...'
        {
            "response": {
                "token": "..."
            }
        }
        """
        # Delete token from redis
        redis.delete(g.token)
        return ResponseBuilder(None, ResponseStatusDict.Deleted).get_response()

    @required_jwt_token
    def get(self):
        """Выдаёт токен содержащийся в jwt указанному токену в GET параметре.

        curl 'http://localhost:5000/v2/tokens' -H 'X-Token: ...'
        {
            "payload": {
                "token": "..."
            }
        }

        Decorators:
            required_jwt_token
        """
        payload = {
            "token": g.token
        }
        return ResponseBuilder(payload, ResponseStatusDict.Success).get_response()
