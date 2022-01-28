"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
# from flask import g, request
from flask_restful import Resource
# from sqlalchemy import func
# from MicroserviceApiIdentity.models import UsersModel
# from MicroserviceApiIdentity.decorators import required_jwt_token, required_schema
# from MicroserviceApiIdentity.db import database
# from MicroserviceApiIdentity.response_builder import ResponseBuilder
# from MicroserviceApiIdentity.dicts import ResponseStatusDict


class TokensServiceResource(Resource):
    def get(self):
        return {}
