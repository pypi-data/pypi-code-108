# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Module for managing azureml-mlflow related Authentication from Azure Machine Learning."""

from azureml.core.authentication import AbstractAuthentication
from azureml.exceptions import AuthenticationException


class DBTokenAuthentication(AbstractAuthentication):

    def __init__(self, db_token):
        self.db_token = db_token

    @property
    def token(self):
        """Databricks token.

        :return: the db_token
        :rtype: str
        """
        return self.db_token

    def get_authentication_header(self):
        """Return the HTTP authorization header.

        The authorization header contains the user access token for access authorization against the service.

        :return: Returns the HTTP authorization header.
        :rtype: dict
        """
        return {"Authorization": "Bearer " + self.db_token}

    def _get_arm_token(self):
        raise AuthenticationException("DBTokenAuthentication._get_arm_token "
                                      "not yet supported.")

    def _get_graph_token(self):
        raise AuthenticationException("DBTokenAuthentication._get_graph_token "
                                      "not yet supported.")
