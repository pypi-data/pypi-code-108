# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Exports experiment run history data to Tensorboard logs suitable for viewing in a Tensorboard instance."""
import os
import logging
from azureml._restclient.experiment_client import ExperimentClient
try:
    import tensorflow as tf
except ImportError:
    print("Could not import tensorflow, required for tensorboard")

module_logger = logging.getLogger(__name__)


def _write_scalar_summary(summary_writer, tag, value, step):
    if tf.executing_eagerly():
        with summary_writer.as_default():
            tf.summary.scalar(tag, value, step=step)
            summary_writer.flush()
    else:
        summary = tf.compat.v1.Summary()
        summary.value.add(tag=tag, simple_value=value)
        summary_writer.add_summary(summary, step)


def export_to_tensorboard(run_data, logsdir, logger=None, recursive=True):
    """Export experiment run history to Tensorboard logs ready for Tensorboard visualization.

    :param run_data: A run or a list of runs to export.
    :type run_data: typing.Union[azureml.core.run.Run,list[azureml.core.run.Run]]
    :param logsdir: A directory path where logs are exported.
    :type logsdir: str
    :param logger: Optional user-specified logger.
    :type logger: logging.Logger
    :param recursive: Specifies whether to recursively retrieve all child runs for specified runs.
    :type recursive: bool

    .. remarks::

        This function enables you to view experiment run history in a Tensorboard instance.
        Use it for Azure Machine learning experiments and other machine learning frameworks that
        don't natively output log files consumable in Tensorboard. For more information
        about using Tensorboard, see `Visualize experiment runs and metrics with
        Tensorboard <https://docs.microsoft.com/azure/machine-learning/how-to-monitor-tensorboard>`_.

        The following example shows how to use the ``export_to_tensorboard`` function to export
        machine learning logs for viewing in TensorBoard. In this example, experiment has completed
        and the run history is stored in Tensorboard logs.

        .. code-block:: python

            # Export Run History to Tensorboard logs
            from azureml.tensorboard.export import export_to_tensorboard
            import os

            logdir = 'exportedTBlogs'
            log_path = os.path.join(os.getcwd(), logdir)
            try:
                os.stat(log_path)
            except os.error:
                os.mkdir(log_path)
            print(logdir)

            # export run history for the project
            export_to_tensorboard(root_run, logdir)

            # or export a particular run
            # export_to_tensorboard(run, logdir)

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/track-and-monitor-experiments/tensorboard/export-run-history-to-tensorboard/export-run-history-to-tensorboard.ipynb


    """
    _logger = logger if logger else module_logger
    if isinstance(run_data, (list,)):
        if not run_data:
            raise Exception("export failed: run_data cannot be empty list")
        runs = run_data
        experiment = run_data[0].experiment
    else:
        try:
            from azureml.core import Run
            # If this is a experiment get all runs
            runs = Run.list(run_data.workspace, run_data.name)
            experiment = run_data
        except AttributeError:
            # Otherwise, this is a run
            runs = [run_data]
            # Note: we assume this method is always scoped to a single project, as discussed with AK
            experiment = run_data.experiment
    if recursive:
        runs += [child for run in runs for child in run.get_children(recursive=True)]
    client = ExperimentClient(experiment.workspace.service_context, experiment.name, experiment.id)

    run_ids = [run.id for run in runs]
    all_metrics = client.get_metrics_by_run_ids(run_ids)
    run_id = None
    writer = None
    for run_metrics in all_metrics:
        old_run_id = run_id
        run_id = run_metrics.run_id
        if old_run_id != run_id:
            logs_file_path = os.path.join(logsdir, run_id)
            if writer is not None:
                writer.close()
            if tf.executing_eagerly():
                writer = tf.summary.create_file_writer(logs_file_path)
            else:
                # Create new file writer for each new runid
                writer = tf.compat.v1.summary.FileWriter(logs_file_path)
        metrics = run_metrics.cells
        step = 0
        for cell in metrics:
            for key, value in cell.items():
                if type(value) == str:
                    _logger.debug(type(value))
                else:
                    _write_scalar_summary(writer, key, value, step)
                    step = step + 1
    if writer is not None:
        writer.close()
