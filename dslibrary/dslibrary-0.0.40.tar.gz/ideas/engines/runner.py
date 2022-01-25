"""
Abstraction of model execution.

Needs to work across all the normal targets:
  * Model Manager
  * mlflow
  * kubeflow, airflow
  * azure ml, sagemaker, gcp
  * kubernetes jobs
  * databricks

project / pipeline / model IDs
point to data sources
configurable engine
run a model
  parameters
  input data
  capture metrics, outputs
  errors
  tracking

this relates to:
  project enumeration
  model storage
"""
import typing


class Project(object):
    def __init__(self, uri: str=None, title: str=None):
        self.uri = uri
        self.title = title


class Pipeline(object):
    def __init__(self, uri: str=None, title: str=None):
        self.uri = uri
        self.title = title


class Model(object):
    def __init__(self, uri: str=None, title: str=None):
        self.uri = uri
        self.title = title


class Run(object):
    def __init__(self, uri: str=None, title: str=None):
        self.uri = uri
        self.title = title
        # TODO contain either a ModelRunner or a PipelineRunner


class ModelManagementEngine(object):
    """
    Top level view of a model management engine.
    """

    def list_projects(self, filters: dict=None) -> typing.Iterable[Project]:
        return []

    def list_pipelines(self, filters: dict=None) -> typing.Iterable[Pipeline]:
        return []

    def list_models(self, filters: dict=None) -> typing.Iterable[Model]:
        return []

    def list_runs(self, filters: dict=None) -> typing.Iterable[Run]:
        return []

    def list_schedules(self):
        # TODO define schedule descriptor
        pass

    # TODO ownership & permissions, esp. of projects & data sources
    # TODO environments
    # TODO configuration of data sources
    #   - when running a model we want to call open_resource("files1:/my_file.csv") and not care whether
    #     it is in s3, abs, or somewhere else
    #   - when calling get_db_connection("my_database") we shouldn't need to know whether it is BigQuery
    #     or PostGres, and what the connection string is
    #   - so....
    #       > we need to manage a set of data sources
    #       > we grant those data sources to models when we run them
    # TODO this is where a feature store would be integrated
    # TODO create/update/delete models & pipelines & data sources

    def model_runner(self, model_uri: str):
        """
        Launching a model begins here.
        """
        return ModelRunner(model_uri)

    def pipeline_runner(self, pipeline_uri: str):
        """
        Launching a pipeline begins here.
        """
        return PipelineRunner(pipeline_uri)


class ModelRunnerX(object):
    """

    """
    def __init__(self, model_uri: str):
        self._model_uri = model_uri
        self._arguments = {}
        self._run_id = None

    def set_argument(self, name: str, value):
        self._arguments[name] = value

    # TODO point to input data

    def start(self):
        # TODO return a tracking object
        pass

    def cancel(self):
        pass

    def wait(self, timeout: float=None):
        pass

    def results(self):
        # TODO return a read-only mmlibrary instance for accessing the inputs, arguments & results
        pass

    # TODO assign a run_id value
    # TODO branching result
    # TODO detect failures & get error detail, logs


class PipelineRunner(object):
    """
    Includes:
      * specification of the workflow (JSON)
      * execution of multiple models in a workflow
      * access to all the individual ModelRunner instances
    """
    def __init__(self, pipeline_uri: str):
        self._pipeline_uri = pipeline_uri

    def start(self):
        pass

    def cancel(self):
        pass
