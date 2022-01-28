"""Copyright (C) 2015-2021 Stack Web Services LLC. All rights reserved."""
import validators
from flask import request
from flask_restful import Resource
from MicroserviceApiIdentity.config import configuration
from MicroserviceApiIdentity.models import UsersModel
from MicroserviceApiIdentity.controllers.users import UsersController
from MicroserviceApiIdentity.controllers.users_recovery_codes import UsersRecoveryCodesController
from MicroserviceApiIdentity import tasks
from MicroserviceApiIdentity.decorators import required_schema
from MicroserviceApiIdentity.response_builder import ResponseBuilder
from MicroserviceApiIdentity.dicts import ResponseStatusDict


class UserPasswordResetResource(Resource):
    @required_schema({
        "type": "object",
        "properties": {
            "email": {"type": "string"}
        },
        "required": [
            "email"
        ]
    })
    def post(self):
        """Запрос сброс пароля.

        Шаг 1: Отправка кода.
        Отправляется письмо на почту с секретным кодом.

        curl -XPOST 'http://procdn.net/api/cdn/0.1/account/password_reset' \
        -H 'content-type: application/json' \
        -d '{"email": "vanzhiganov@ya.ru"}'

        **JSONSchema**

            {
                "email": "vanzhiganov@ya.ru"
            }
        """
        email = request.json.get('email')
        # TODO: возможно надо будет убрать, так как jsonschema проверяет наличие
        if not email:
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0107).get_response()
        # validate email
        if not validators.email(email) or not UsersModel.is_exists_email(email):
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0106).get_response()
        #
        if configuration.getboolean('celery', 'enabled'):
            tasks.send_email_password_recovery_code.delay(email)
        else:
            tasks.send_email_password_recovery_code(email)
        return ResponseBuilder(None, ResponseStatusDict.Success).get_response()

    @required_schema({
        "type": "object",
        "properties": {
            "email": {"type": "string"},
            "recovery_code": {"type": "string"}
        },
        "required": ["email", "recovery_code"]
    })
    def put(self):
        """Проверка наличия кода.

        Шаг 2: Смена пароля
        После успешного выполнения запроса пользователю отправляется письмо
        с сообщением о смене пароля

        curl -XPOST 'http://procdn.net/api/cdn/0.1/account/password_reset' \
        -H 'content-type: application/json' \
        -d '{"email": "vanzhiganov@ya.ru", "recovery_code": "..."}'
        """
        email = request.json.get('email')
        recovery_code = request.json.get('recovery_code')

        if not email:
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0107).get_response()

        # validate email
        if not validators.email(email):
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0106).get_response()
        # validate email
        if not UsersModel.is_exists_email(email):
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0108).get_response()

        user = UsersModel.get_item_by_email(email)

        # check valid recovery codes
        if not UsersRecoveryCodesController().check(user.id, recovery_code):
            return ResponseBuilder(None, ResponseStatusDict.MS_ID_0109).get_response()

        # remove old recovery codes for user
        UsersRecoveryCodesController().delete(user.id)

        # generate new password
        new_password = UsersController().generate_password()

        # save password
        UsersController().update(user.id, password=new_password)

        if configuration.getboolean('celery', 'enabled'):
            tasks.send_email_password_reseted.delay(email, new_password)
        else:
            tasks.send_email_password_reseted(email, new_password)

        return ResponseBuilder(None, ResponseStatusDict.Success).get_response()
