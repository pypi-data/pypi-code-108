"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""

import validators
from flask import request
from flask_restful import Resource
from MicroserviceApiIdentity.config import configuration
from MicroserviceApiIdentity.db import database
from MicroserviceApiIdentity.models import UsersModel
from MicroserviceApiIdentity.decorators import required_schema
from MicroserviceApiIdentity.tasks import send_email_registration
from MicroserviceApiIdentity.response_builder import ResponseBuilder
from MicroserviceApiIdentity.dicts import ResponseStatusDict


class UsersResource(Resource):
    @required_schema({
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "format": "email"
            },
            "password": {
                "type": "string",
                "minLength": 5
            }
        },
        "required": [
            "email",
            "password"
        ]
    })
    def post(self):
        email = request.json.get("email")
        password = request.json.get("password")

        # check valid email
        if not validators.email(email):
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0102).get_response()
        # TODO: разработать правила сложности пароля
        if len(password) < 5:
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0103).get_response()

        # count user with email and password
        if UsersModel.is_exists_email(email):
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0104).get_response()

        user = UsersModel(email, UsersModel.get_hash(password), is_enabled=1)
        try:
            database.session.add(user)
            database.session.commit()
        except Exception as e:
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0105).get_response()

        if configuration.getboolean('celery', 'enabled'):
            send_email_registration.delay(email, password)
        else:
            # TODO: сделать проверку на ошибку
            # TODO: сделать проверку параметра отправки почты при создании пользователя Администратором
            send_email_registration(email, password)

        return ResponseBuilder(None, ResponseStatusDict.MS_ID_0001).get_response()
