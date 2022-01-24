# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Defines Part B of the logging schema, optional keys that have a common meaning across telemetry data."""
from typing import Any, List
from enum import Enum

from azureml._common._error_response._error_response_constants import ErrorCodes


class StandardFieldKeys:
    """Keys for standard fields."""

    ALGORITHM_TYPE_KEY = 'AlgorithmType'
    CLIENT_OS_KEY = 'ClientOS'
    COMPUTE_TYPE_KEY = 'ComputeType'
    FAILURE_REASON_KEY = 'FailureReason'
    ITERATION_KEY = 'Iteration'
    TASK_RESULT_KEY = 'TaskResult'
    PARENT_RUN_ID_KEY = 'ParentRunId'
    PARENT_RUN_UUID_KEY = 'ParentRunUuid'
    RUN_ID_KEY = 'RunId'
    RUN_UUID_KEY = 'RunUuid'
    WORKSPACE_REGION_KEY = 'WorkspaceRegion'
    DURATION_KEY = 'Duration'

    @classmethod
    def keys(cls) -> List[str]:
        """Keys for standard fields."""
        return [
            StandardFieldKeys.ALGORITHM_TYPE_KEY,
            StandardFieldKeys.CLIENT_OS_KEY,
            StandardFieldKeys.COMPUTE_TYPE_KEY,
            StandardFieldKeys.FAILURE_REASON_KEY,
            StandardFieldKeys.ITERATION_KEY,
            StandardFieldKeys.TASK_RESULT_KEY,
            StandardFieldKeys.PARENT_RUN_ID_KEY,
            StandardFieldKeys.PARENT_RUN_UUID_KEY,
            StandardFieldKeys.RUN_ID_KEY,
            StandardFieldKeys.RUN_UUID_KEY,
            StandardFieldKeys.WORKSPACE_REGION_KEY,
            StandardFieldKeys.DURATION_KEY
        ]


class ComputeType(Enum):
    # AzureML compute
    AmlcTrain = 1  # Azure machine learning compute Training cluster, aka. BatchAI, Machine learning compute
    AmlcInference = 2  # Azure machine learning compute Inference cluster
    AmlcDsi = 3  # Azure machine learning compute Data sciense instance
    # non AzureML compute, aka attached compute
    Remote = 4  # use this if you are not sure the type of your attached VM
    VirtualMachine = 4  # alias of Remote
    AzureDatabricks = 5,
    HdiCluster = 6
    HDInsight = 6
    AKS = 7  # Azure Kubernetes Service
    ADLA = 8  # Azure Data Lake Analytics, attached compute
    ACI = 9  # Azure Container Instance
    ContainerInstance = 9
    # DSVM rp
    DSVM = 20  # Data Sciense VM
    # BatchAI rp
    BatchAI = 30
    # Local
    Local = 50

    Others = 100


class AlgorithmType(Enum):
    Classification = 1
    Regression = 2
    Forecasting = 3
    Ranking = 4
    Others = 100


class TaskResult(Enum):
    Success = 1
    Failure = 2
    Cancelled = 3
    Others = 100


class FailureReason(Enum):
    UserError = 1
    SystemError = 2


def _str_to_enum(cls: type, s: str = None, default=None):
    if s is None:
        return None
    elif hasattr(cls, s):
        return cls[s]
    elif default is not None:
        return default
    elif hasattr(cls, "Others"):
        return cls.Others
    else:
        return None


class StandardFields(dict):
    """Defines Part B of the logging schema, optional keys that have a common meaning across telemetry data."""

    def __init__(self, algorithm_type: AlgorithmType = None, client_os: str = None,
                 compute_type: ComputeType = None, iteration=None, run_id=None, parent_run_id=None,
                 task_result: TaskResult = None, failure_reason: FailureReason = None, workspace_region=None,
                 duration=None, *args: Any, **kwargs: Any):
        """Initialize a new instance of the StandardFields."""
        super(StandardFields, self).__init__(*args, **kwargs)
        self.algorithm_type = algorithm_type
        self.client_os = client_os
        self.compute_type = compute_type
        self.failure_reason = failure_reason
        self.iteration = iteration
        self.run_id = run_id
        self.parent_run_id = parent_run_id
        self.task_result = task_result
        self.workspace_region = workspace_region
        self.duration = duration

    def _set_field(self, key: str, value):
        if value is None:
            self.pop(key, None)
        else:
            self[key] = value

    def _set_enum_field(self, enum_cls: type, value, key=None):
        if value is None:
            val = None
        elif type(value) == enum_cls:
            val = value.name
        elif type(value) == str:
            val = _str_to_enum(enum_cls, value).name
        else:
            val = None
        if val is None:
            self.pop(key or enum_cls.__name__, None)
        else:
            self[key or enum_cls.__name__] = val

    def _get_enum_field(self, enum_cls: type, key=None):
        val = self.get(key or enum_cls.__name__, None)
        return None if val is None else enum_cls[val]

    @property
    def algorithm_type(self) -> AlgorithmType:
        """Component name."""
        return self._get_enum_field(AlgorithmType)

    @algorithm_type.setter
    def algorithm_type(self, value: AlgorithmType):
        """
        Set component name.

        :param value: Value to set to.
        """
        self._set_enum_field(AlgorithmType, value)

    @property
    def client_os(self) -> str:
        """Get the client operating system."""
        return self.get(StandardFieldKeys.CLIENT_OS_KEY, None)

    @client_os.setter
    def client_os(self, value: str):
        """
        Set the client operating system.

        :param value: Value to set to.
        """
        self._set_field(StandardFieldKeys.CLIENT_OS_KEY, value)

    @property
    def compute_type(self) -> ComputeType:
        """Compute Type."""
        return self._get_enum_field(ComputeType)

    @compute_type.setter
    def compute_type(self, value):
        """
        Set compute type.

        :param value: Value to set to.
        """
        self._set_enum_field(ComputeType, value)

    @property
    def failure_reason(self) -> FailureReason:
        """Get failure reason."""
        return self._get_enum_field(FailureReason)

    @failure_reason.setter
    def failure_reason(self, value: FailureReason):
        """Set failure reason."""
        validate = value is None or type(value) == FailureReason\
            or value == ErrorCodes.USER_ERROR or value == ErrorCodes.SYSTEM_ERROR
        assert validate, "Failure reason has to be either User or System"
        self._set_enum_field(FailureReason, value)

    @property
    def iteration(self) -> int:
        """ID for iteration."""
        return self.get(StandardFieldKeys.ITERATION_KEY, None)

    @iteration.setter
    def iteration(self, value: int):
        """
        Set iteration ID.

        :param value: Value to set to.
        """
        self._set_field(StandardFieldKeys.ITERATION_KEY, value)

    @property
    def task_result(self) -> TaskResult:
        """Job status."""
        return self._get_enum_field(TaskResult)

    @task_result.setter
    def task_result(self, value: TaskResult):
        """
        Set job status.

        :param value: Value to set to.
        """
        self._set_enum_field(TaskResult, value)

    @property
    def parent_run_id(self) -> str:
        """Parent run ID."""
        return self.get(StandardFieldKeys.PARENT_RUN_ID_KEY, None)

    @parent_run_id.setter
    def parent_run_id(self, value: str):
        """
        Set parent run ID.

        :param value: Value to set to.
        """
        self._set_field(StandardFieldKeys.PARENT_RUN_ID_KEY, value)

    @property
    def parent_run_uuid(self) -> str:
        """Parent run UUID."""
        return self.get(StandardFieldKeys.PARENT_RUN_UUID_KEY, None)

    @parent_run_uuid.setter
    def parent_run_uuid(self, value: str):
        """
        Set parent run UUID.

        :param value: Value to set to.
        """
        self._set_field(StandardFieldKeys.PARENT_RUN_UUID_KEY, value)

    @property
    def run_id(self) -> str:
        """Run ID."""
        return self.get(StandardFieldKeys.RUN_ID_KEY, None)

    @run_id.setter
    def run_id(self, value: str):
        """
        Set run ID.

        :param value: Value to set to.
        """
        self._set_field(StandardFieldKeys.RUN_ID_KEY, value)

    @property
    def run_uuid(self) -> str:
        """Run UUID."""
        return self.get(StandardFieldKeys.RUN_UUID_KEY, None)

    @run_uuid.setter
    def run_uuid(self, value: str):
        """
        Set run UUID.

        :param value: Value to set to.
        """
        self._set_field(StandardFieldKeys.RUN_UUID_KEY, value)

    @property
    def workspace_region(self) -> str:
        """Workspace region."""
        return self.get(StandardFieldKeys.WORKSPACE_REGION_KEY, None)

    @workspace_region.setter
    def workspace_region(self, value: str):
        """
        Set Workspace region.

        :param value: Value to set to.
        """
        self._set_field(StandardFieldKeys.WORKSPACE_REGION_KEY, value)

    @property
    def duration(self) -> float:
        """Duration in ms."""
        return self.get(StandardFieldKeys.DURATION_KEY, None)

    @duration.setter
    def duration(self, value: float):
        """
        Set duration in ms.

        :param value: Value to set to.
        """
        self._set_field(StandardFieldKeys.DURATION_KEY, value)
