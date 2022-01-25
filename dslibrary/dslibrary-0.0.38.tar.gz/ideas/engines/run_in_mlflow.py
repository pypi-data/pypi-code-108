"""
A model management engine that wraps MLFlow.  We have the option of using MLFlow only for tracking, or for
both tracking and execution.

When using for tracking only, the model communicates with the engine over REST and the engine calls MLFlow on its
behalf.  When using for both tracking and execution, the model calls mmlibrary, which delegates to MLFlow for some
tasks (like reporting metrics), but calls back to the engine for others, like accessing input data.
"""
import os
import tempfile

from mmlibrary.front import MMLibrary, Metric
from mmlibrary.metadata import Metadata

try:
    import mlflow
except ImportError:
    mlflow = None

IMAGE_EXTENSIONS = ("png", "jpg", "jpeg", "gif")


class RunInMLFlow(object):
    def run(self):
        pass


class MMLibraryToMLFlow(MMLibrary):
    """
    The executing model calls the main MMLibrary entry points, which transfer control, one way or another,
    to this class.

    Here, we call MLFlow methods on the running model's behalf.

    WILL MLFLOW BE EXECUTING THE MODELS?  Not necessarily.
      - if it is, then hopefully it doesn't mind the tracking calls coming from an unexpected host
      - if it isn't, then we will need to delegate the run() calls somewhere

    If supplied, input data requests are delegated to data_handler.
    """
    def __init__(self, data_handler=None, execution_handler=None):
        if not mlflow:
            raise Exception("The 'mlflow' package is required to use this interface")
        self._data_handler = data_handler
        self._execution_handler = execution_handler
        self._run = None
        self._experiment_id = self._run.info.experiment_id

    def get_metadata(self, other_model_uri: str=None) -> Metadata:
        # TODO URI & metadata needed for model being executed
        return Metadata()

    def start(self):
        self._run = mlflow.active_run()
        return mlflow.start_run()

    def end(self):
        return mlflow.end_run()

    def open_resource(self, resource_name: str, mode: str = 'r', context_uri: str=None):
        if "r" in mode:
            if self._data_handler:
                return self._data_handler.open_resource(resource_name, mode, context_uri)
            # TODO error -
        else:
            # TODO capture the content, then on close() call write_resource()
            pass

    def write_resource(self, filename: str, content=None, append: bool=False, target_path: str=None):
        """
        All the output is redirected to mlflow.
        :param filename:
        :param content:
        :param append:
        :param target_path:
        :return:
        """
        target_filename = self._target_filename(filename, target_path)
        file_extn = os.path.splitext(filename)[1].strip(".").lower()
        target_extn = os.path.splitext(target_path or "")[1].strip(".").lower()
        if isinstance(content, dict):
            return mlflow.log_dict(content, target_filename)
        if isinstance(content, str):
            return mlflow.log_text(content, target_filename)
        if file_extn in IMAGE_EXTENSIONS or target_extn in IMAGE_EXTENSIONS:
            if content is None:
                with open(filename, 'rb') as f_r:
                    content = f_r.read()
            return mlflow.log_image(content, target_filename)
        if hasattr(content, "savefig"):
            return mlflow.log_figure(content, target_filename)
        if content is not None:
            with tempfile.NamedTemporaryFile(mode='w' if isinstance(content, str) else 'wb') as f_tmp:
                f_tmp.write(content)
            mlflow.log_artifact(f_tmp.name, filename or target_path)
        else:
            mlflow.log_artifact(filename, target_path)

    def save_metric(self, metric_name: str, metric_value):
        # TODO mlflow adds 'step', which disambiguates among metrics with the same name from the same run
        mlflow.log_metric(metric_name, metric_value)

    def save_metrics(self, metrics: dict) -> None:
        mlflow.log_metrics(metrics)

    def get_metrics(self, metric_name: str = None, uri: str = None, time_range: (list, tuple) = None, limit: int = None):
        if uri or time_range or limit:
            # TODO finish implementing this
            pass
        run = mlflow.get_run(self._run.info.run_id)
        metrics = run.data.metrics
        t0 = run.start_time
        for k, v in metrics.items():
            yield Metric(run_id=self._run.info.run_id, uri=self._experiment_id, time=t0, name=k, value=v)

    def get_db_connection(self, connection_name: str, database: str = None):
        if self._data_handler:
            # TODO returning a DBI interface over REST won't do.  I think we need a more clever means of delegation here
            return self._data_handler.get_sql_connection(connection_name, database)
        # TODO error, no data handler

    def run(self, code_uri: str, arguments: dict = None, callback=None):
        if self._execution_handler:
            # TODO the callback won't work over REST, of course...
            return self._execution_handler.run(code_uri, arguments, callback)
        # TODO translate call into MLFlow-ese...
        #  mlflow.run(uri, entry_point='main', version=None, parameters=None, docker_args=None, experiment_name=None, experiment_id=None, backend='local', backend_config=None, use_conda=True, storage_dir=None, synchronous=True, run_id=None)
