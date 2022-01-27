"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
from flask import g, request
from flask_restful import Resource
from MicroserviceApiIdentity.config import configuration
from MicroserviceApiIdentity.models import UsersModel
from MicroserviceApiIdentity.controllers.users import UsersController
from MicroserviceApiIdentity.tasks import send_email_password_updated
from MicroserviceApiIdentity.decorators import required_jwt_token, required_schema
from MicroserviceApiIdentity.response_builder import ResponseBuilder
from MicroserviceApiIdentity.dicts import ResponseStatusDict


class UserPasswordUpdateResource(Resource):
    @required_jwt_token
    @required_schema({
        'type': 'object',
        'properties': {
            'new_password': {'type': 'string'},
            'old_password': {'type': 'string'},
        },
        'required': ['new_password', 'old_password']
    })
    def post(self):
        """Обновление пароля"""
        user_id = g.account['id']
        email = g.account['email']
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')

        if not new_password or not old_password:
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0110).get_response()

        # Проверка старого пароля
        if not UsersModel.auth(email, old_password):
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0111).get_response()

        # Обновляем пароль
        UsersController().update(user_id, password=new_password)

        # Отложенная задача отправки сообщения
        if configuration.getboolean('celery', 'enabled'):
            send_email_password_updated.delay(email, new_password)
        else:
            send_email_password_updated(email, new_password)

        return ResponseBuilder(None, ResponseStatusDict.Success).get_response()
