# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from azureml.responsibleai.tools.model_analysis._requests.request_dto import RequestDTO


class ComputeDTO:
    def __init__(self,
                 experiment_name: str,
                 model_analysis_run_id: str,
                 requests: RequestDTO
                 ):
        self._experiment_name = experiment_name
        self._model_analysis_run_id = model_analysis_run_id
        self._requests = requests

    @property
    def experiment_name(self) -> str:
        return self._experiment_name

    @property
    def model_analysis_run_id(self) -> str:
        return self._model_analysis_run_id

    @property
    def requests(self) -> RequestDTO:
        return self._requests
