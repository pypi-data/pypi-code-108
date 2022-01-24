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
from .job import Job
from .shap_matrix import ShapMatrix


class ShapMatrixJob(Job):
    def __init__(self, data, model_id, dataset_id, **kwargs):
        super(Job, self).__init__(data, **kwargs)
        self._model_id = model_id
        self._dataset_id = dataset_id

    @classmethod
    def get(cls, project_id, job_id, model_id=None, dataset_id=None):
        """
        Fetches one SHAP matrix job.

        Parameters
        ----------
        project_id : str
            The identifier of the project in which the job resides
        job_id : str
            The job identifier
        model_id : str
            The identifier of the model used for computing prediction explanations
        dataset_id : str
            The identifier of the dataset against which prediction explanations should be computed

        Returns
        -------
        job : ShapMatrixJob
            The job

        Raises
        ------
            AsyncFailureError
                Querying this resource gave a status code other than 200 or 303
        """
        url = cls._job_path(project_id, job_id)
        data, completed_url = cls._data_and_completed_url_for_job(url)
        return cls(
            data, model_id=model_id, dataset_id=dataset_id, completed_resource_url=completed_url,
        )

    def _make_result_from_location(self, location, params=None):
        return ShapMatrix.from_location(
            location, model_id=self._model_id, dataset_id=self._dataset_id,
        )

    def refresh(self):
        """
        Update this object with the latest job data from the server.
        """
        data, completed_url = self._data_and_completed_url_for_job(self._this_job_path())
        self.__init__(
            data,
            model_id=self._model_id,
            dataset_id=self._dataset_id,
            completed_resource_url=completed_url,
        )
