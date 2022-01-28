"""Copyright (C) 2015-2021 Stack Web Services LLC. All rights reserved."""
from flask import g, request
from flask_restful import Resource
from MicroserviceApiIdentity.models import DetailsModel
from MicroserviceApiIdentity.db import database
from MicroserviceApiIdentity.decorators import required_jwt_token, required_schema
from MicroserviceApiIdentity.response_builder import ResponseBuilder
from MicroserviceApiIdentity.dicts import ResponseStatusDict


class UserDetailsResource(Resource):
    """Restful Billing balance resource"""
    @required_jwt_token
    def get(self):
        """Account details"""
        user_id = g.account['id']
        # проверяем, есть ли запись в таблице usersdetails, чтобы небыло ошибок
        if not DetailsModel.is_exists_user(user_id):
            # если нет, то делаем запись в таблицу, чтобы небыло ошибок
            # DetailsModel.create(user=user_id)
            details = DetailsModel(user_id)
            database.session.add(details)
            database.session.commit()
        else:
            # извлекаем из базы детали пользователя
            details = DetailsModel.get_item(user_id)

        # build result
        payload = {
            "fname": details.fname or '',
            "lname": details.lname or '',
            "address": details.address or '',
            "city": details.city or '',
            "country": details.country or '',
            "state": details.state or '',
            "zipcode": details.zipcode or '',
        }

        return ResponseBuilder(payload, ResponseStatusDict.Success).get_response()

    @required_jwt_token
    @required_schema({
        "type": "object",
        "properties": {
        }
    })
    def post(self):
        """Update account details fields"""
        fields = ['fname', 'lname', 'address', 'city', 'country', 'state', 'zipcode']

        data = {}
        for i in request.json:
            if i not in fields:
                continue
            data[i] = request.json.get(i)

        database.session.query(DetailsModel).filter_by(user=g.account['id']).update(data)
        database.session.commit()

        return ResponseBuilder(None, ResponseStatusDict.Success).get_response()
