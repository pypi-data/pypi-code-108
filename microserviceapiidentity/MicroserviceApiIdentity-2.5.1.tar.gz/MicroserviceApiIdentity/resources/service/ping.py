"""Copyright (C) 2015-2022 Stack Web Services LLC. All rights reserved."""
import pkg_resources
# from flask import g, request
from flask_restful import Resource
from sqlalchemy import func
from MicroserviceApiIdentity.models import UsersModel
# from MicroserviceApiIdentity.decorators import required_jwt_token, required_schema
from MicroserviceApiIdentity.db import database
from MicroserviceApiIdentity.response_builder import ResponseBuilder
from MicroserviceApiIdentity.dicts import ResponseStatusDict


class PingServiceResource(Resource):
    @staticmethod
    def packages() -> list:
        """Get installed packages in current environment
        >>> PingServiceResource.packages()
        ['absl-py==0.7.0', 'adodbapi==2.6.0.7']
        """
        installed_packages = pkg_resources.working_set
        installed_packages_list = sorted(
            ["%s==%s" % (i.key, i.version) for i in installed_packages])
        return installed_packages_list

    @staticmethod
    def check_database() -> bool:
        """
        >>> PingServiceResource.check_database()
        True
        """
        try:
            database.session.query(func.count(UsersModel.id).label("records")).scalar()
        except Exception as e:
            return False
        else:
            return True

    def get(self):
        return ResponseBuilder({
            'services': {
                'database': self.check_database()
            },
            'packages': self.packages(),
        }, ResponseStatusDict.Success).get_response()
