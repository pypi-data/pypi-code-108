from enum import Enum


class WorkflowType(Enum):
    """
    Type of workflow in place. This is useful to differentiate
    between the script and blueprint workflows.
    """
    SCRIPT = 'script'
    BLUEPRINT = 'blueprint'


class ObservableType(Enum):
    """
    Observable types of objects from Grid. These objects can be followed
    with status.
    """
    CLUSTER = 'cluster'
    RUN = 'run'
    EXPERIMENT = 'experiment'
    INTERACTIVE = 'interactive'
