"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
from flask import g, request
from flask_restful import Resource
from MicroserviceApiIdentity.models import SecretsModel
from MicroserviceApiIdentity.decorators import required_jwt_token, required_schema
from MicroserviceApiIdentity.db import database
from MicroserviceApiIdentity.response_builder import ResponseBuilder
from MicroserviceApiIdentity.dicts import ResponseStatusDict


class SecretResource(Resource):
    """Token endpoint class"""
    @required_jwt_token
    def get(self):
        user_id = g.account['id']

        secrets = database.session.query(
            SecretsModel.secret,
            SecretsModel.acl,
            SecretsModel.status
        ).filter_by(user=user_id).all()

        payload = []
        for secret in secrets:
            payload.append({
                "secret": secret.secret,
                "acl": secret.acl,
                "status": secret.status
            })
        return ResponseBuilder(payload, ResponseStatusDict.Success).get_response()
    
    @required_jwt_token
    @required_schema({
        "type": "object",
        "properties": {
            "secret": {
                "type": "string"
            },
        },
        "required": [
            "secret"
        ]
    })
    def post(self):
        """

        :return:
        """
        # # TODO: if new_secret is empty then return 400 http code (bad request)
        #
        # secret = SecretsModel(g.account['id'])
        # secret.secret = request.json.get('secret')
        # secret.acl = ""
        # secret.status = 1
        #
        # database.session.add(secret)
        # database.session.commit()

        # TODO: if new_secret is empty then return 400 http code (bad request)
        secret = database.session.query(SecretsModel).filter_by(user=g.account['id']).first()
        if not secret:
            secret = SecretsModel(g.account['id'])
            secret.secret = request.json.get('secret')
            secret.acl = ""
            secret.status = 1
            database.session.add(secret)
        else:
            secret.secret = request.json.get('secret')

        database.session.commit()

        return ResponseBuilder(None, ResponseStatusDict.Updated).get_response()

    @required_jwt_token
    def delete(self):
        """

        :return:
        """
        # TODO: ...

        return ResponseBuilder(None, ResponseStatusDict.Deleted).get_response()
