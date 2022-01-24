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

from datarobot._compat import String
from datarobot.models.api_object import APIObject
from datarobot.utils import encode_utf8_if_py2
from datarobot.utils.pagination import unpaginate


class PayoffMatrix(APIObject):
    """ Represents a Payoff Matrix, a costs/benefit scenario used for creating a profit curve.

    Attributes
    ----------
    project_id : str
        id of the project with which the payoff matrix is associated.
    id : str
        id of the payoff matrix.
    name : str
        User-supplied label for the payoff matrix.
    true_positive_value : float
        Cost or benefit of a true positive classification
    true_negative_value: float
        Cost or benefit of a true negative classification
    false_positive_value: float
        Cost or benefit of a false positive classification
    false_negative_value: float
        Cost or benefit of a false negative classification

    Examples
    --------
    .. code-block:: python

        import datarobot as dr

        # create a payoff matrix
        payoff_matrix = dr.PayoffMatrix.create(project_id, name, true_positive_value=100,
                        true_negative_value=10, false_positive_value=0, false_negative_value=-10)

        # list available payoff matrices
        payoff_matrices = dr.PayoffMatrix.list(project_id)
        payoff_matrix = payoff_matrices[0]
    """

    _base_url = "projects/{}/payoffMatrices/"
    _payoff_matrix_url = _base_url + "{}/"
    _converter = t.Dict(
        {
            t.Key("id"): String(),
            t.Key("project_id"): String(),
            t.Key("name"): String(),
            t.Key("true_positive_value"): t.Float(),
            t.Key("true_negative_value"): t.Float(),
            t.Key("false_positive_value"): t.Float(),
            t.Key("false_negative_value"): t.Float(),
        }
    ).ignore_extra("*")

    def __init__(
        self,
        project_id,
        id,
        name=None,
        true_positive_value=None,
        true_negative_value=None,
        false_positive_value=None,
        false_negative_value=None,
    ):
        self.project_id = project_id
        self.id = id
        self.name = name
        self.true_positive_value = true_positive_value
        self.true_negative_value = true_negative_value
        self.false_positive_value = false_positive_value
        self.false_negative_value = false_negative_value

    def __repr__(self):
        template = (
            u"{}(id={!r}, project_id={!r}, name={!r}, true_positive_value={!r}, "
            u"true_negative_value={!r}, false_positive_value={!r}, "
            u"false_negative_value={!r})"
        )
        return encode_utf8_if_py2(
            template.format(
                type(self).__name__,
                self.id,
                self.project_id,
                self.name,
                self.true_positive_value,
                self.true_negative_value,
                self.false_positive_value,
                self.false_negative_value,
            )
        )

    @classmethod
    def create(
        cls,
        project_id,
        name,
        true_positive_value=1,
        true_negative_value=1,
        false_positive_value=-1,
        false_negative_value=-1,
    ):
        """
        Create a payoff matrix associated with a specific project.

        Parameters
        ----------
        project_id : str
            id of the project with which the payoff matrix will be associated

        Returns
        -------
        payoff_matrix : :py:class:`PayoffMatrix <datarobot.models.PayoffMatrix>`
            The newly created payoff matrix
        """
        data = {
            "name": name,
            "true_positive_value": true_positive_value,
            "true_negative_value": true_negative_value,
            "false_positive_value": false_positive_value,
            "false_negative_value": false_negative_value,
        }

        url = cls._base_url.format(project_id)
        response = cls._client.post(url, data=data)
        return cls.from_server_data(response.json())

    @classmethod
    def list(cls, project_id):
        """
        Fetch all the payoff matrices for a project.

        Parameters
        ----------
        project_id : str
            id of the project
        Returns
        -------
        List of PayoffMatrix
            A list of :py:class:`PayoffMatrix <datarobot.models.PayoffMatrix>` objects
        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        data = unpaginate(
            initial_url=cls._base_url.format(project_id), initial_params=None, client=cls._client,
        )
        result = [cls.from_server_data(item) for item in data]
        return result

    @classmethod
    def get(cls, project_id, id):
        """
        Retrieve a specified payoff matrix.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        id : str
            id of the payoff matrix

        Returns
        -------
        :py:class:`PayoffMatrix <datarobot.models.PayoffMatrix>` object representing specified
        payoff matrix

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        return cls.from_location("/projects/{}/payoffMatrices/{}".format(project_id, id))

    @classmethod
    def update(
        cls,
        project_id,
        id,
        name,
        true_positive_value,
        true_negative_value,
        false_positive_value,
        false_negative_value,
    ):
        """ Update (replace) a payoff matrix. Note that all data fields are required.

        Parameters
        ----------
        project_id : str
            id of the project to which the payoff matrix belongs
        id : str
            id of the payoff matrix
        name : str
            User-supplied label for the payoff matrix
        true_positive_value : float
            True positive payoff value to use for the profit curve
        true_negative_value : float
            True negative payoff value to use for the profit curve
        false_positive_value : float
            False positive payoff value to use for the profit curve
        false_negative_value : float
            False negative payoff value to use for the profit curve

        Returns
        -------
        payoff_matrix
            PayoffMatrix with updated values

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        data = {
            "name": name,
            "truePositiveValue": true_positive_value,
            "trueNegativeValue": true_negative_value,
            "falsePositiveValue": false_positive_value,
            "falseNegativeValue": false_negative_value,
        }

        url = "projects/{}/payoffMatrices/{}/".format(project_id, id)
        response = cls._client.put(url, json=data)
        return cls.from_server_data(response.json())

    @classmethod
    def delete(cls, project_id, id):
        """
        Delete a specified payoff matrix.

        Parameters
        ----------
        project_id : str
            id of the project the model belongs to
        id : str
            id of the payoff matrix

        Returns
        -------
        response : requests.Response
            Empty response (204)

        Raises
        ------
        datarobot.errors.ClientError
            if the server responded with 4xx status
        datarobot.errors.ServerError
            if the server responded with 5xx status
        """
        url = cls._payoff_matrix_url.format(project_id, id)
        return cls._client.delete(url)
