#
# Copyright 2021 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
import trafaret as t

from datarobot._compat import Int, String
from datarobot.models.api_object import APIObject


class PrimeFile(APIObject):
    """ Represents an executable file available for download of the code for a DataRobot Prime model

    Attributes
    ----------
    id : str
        the id of the PrimeFile
    project_id : str
        the id of the project this PrimeFile belongs to
    parent_model_id : str
        the model being approximated by this PrimeFile
    model_id : str
        the prime model this file represents
    ruleset_id : int
        the ruleset being used in this PrimeFile
    language : str
        the language of the code in this file - see enums.LANGUAGE for possibilities
    is_valid : bool
        whether the code passed basic validation
    """

    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("project_id"): String(),
            t.Key("parent_model_id"): String(),
            t.Key("model_id"): String(),
            t.Key("ruleset_id"): Int(),
            t.Key("language"): String(),
            t.Key("is_valid"): t.Bool(),
        }
    ).allow_extra("*")

    def __init__(
        self,
        id=None,
        project_id=None,
        parent_model_id=None,
        model_id=None,
        ruleset_id=None,
        language=None,
        is_valid=None,
    ):
        self.id = id
        self.project_id = project_id
        self.parent_model_id = parent_model_id
        self.model_id = model_id
        self.ruleset_id = ruleset_id
        self.language = language
        self.is_valid = is_valid

    @classmethod
    def get(cls, project_id, file_id):
        url = "projects/{}/primeFiles/{}/".format(project_id, file_id)
        return cls.from_location(url)

    def download(self, filepath):
        """ Download the code and save it to a file

        Parameters
        ----------
        filepath: string
            the location to save the file to
        """
        url = "projects/{}/primeFiles/{}/download/".format(self.project_id, self.id)
        response = self._client.get(url)
        with open(filepath, mode="wb") as out_file:
            out_file.write(response.content)
