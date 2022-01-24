# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Common widget implementations shared between various platforms."""
import importlib

from azureml.widgets._telemetry_logger import _TelemetryLogger

from . import _platform

# Jupyter Notebook
if _platform._in_jupyter_nb() is True:
    PLATFORM = 'JUPYTER'
# Databricks and others
else:
    PLATFORM = 'DATABRICKS'

logger = _TelemetryLogger.get_telemetry_logger(__name__)


def _create_rundetails_importer(run_type, class_name):
    def _soft_import_impl():
        mod_name = "azureml.widgets._{}._run_details".format(run_type)
        mod = importlib.import_module(mod_name)
        assert mod
        class_ref = getattr(mod, class_name)
        assert class_ref
        return class_ref
    return _soft_import_impl


class RunDetails:
    """
    Represents a Jupyter notebook widget used to view the progress of model training.

    A widget is asynchronous and provides updates until training finishes.

    :param run_instance: Run instance for which the widget will be rendered.
    :type run_instance: azureml.core.run.Run

    .. remarks::

        An Azure ML Jupyter Notebook widget shows the progress of model training, including properties, logs, and
        metrics. The selected widget type is inferred implicitly from the ``run_instance``. You don't need to set it
        explicitly. Use the :meth:`show` method to begin rendering of the widget. If the widget isn't installed,
        you'll instead see a link to view the content in a new browser page. After starting an experiment, you can
        also see the progress of model training in the Azure portal using the ``get_portal_url()`` method of
        the :class:`azureml.core.Run` class.

        The following example shows how to create a widget and start it:

        .. code-block:: python

            from azureml.widgets import RunDetails
            RunDetails(remote_run).show()

        Full sample is available from
        https://github.com/Azure/MachineLearningNotebooks/blob/master/how-to-use-azureml/automated-machine-learning/classification-credit-card-fraud/auto-ml-classification-credit-card-fraud.ipynb


        The following types of runs are supported:

        * :class:`azureml.pipeline.core.StepRun`: Shows run properties, output logs, metrics.
        * :class:`azureml.train.hyperdrive.HyperDriveRun`: Shows parent run properties, logs, child runs, primary
          metric chart, and parallel coordinate chart of hyperparameters.
        * :class:`azureml.train.automl.run.AutoMLRun`: Shows child runs and primary metric chart with option to select
          individual metrics.
        * :class:`azureml.pipeline.core.run.PipelineRun`: Shows running and non-running nodes of a pipeline along
          with graphical representation of nodes and edges.
        * :class:`azureml.contrib.train.rl.ReinforcementLearningRun`: Shows status of runs in real time.
          Azure Machine Learning Reinforcement Learning
          is currently a preview feature. For more information, see `Reinforcement learning with Azure Marchine
          Learning <https://docs.microsoft.com/azure/machine-learning/how-to-use-reinforcement-learning>`_.

        The `azureml-widgets` package is installed when you install the Azure Machine Learning SDK. However, some
        further installation may be needed depending on environment.

        * Jupyter Notebooks: Both local and cloud notebooks are fully supported, with interactivity, async
          auto-updates, and non-blocking cell execution.
        * JupyterLab: Some further installation may be needed.
            1. Verify that the `azure-widgets` package is installed and if not, install it.

               .. code-block:: shell

                    sudo -i pip install azureml-widgets

            1. Install JupyterLab Extension.

              .. code-block:: shell

                    sudo -i jupyter labextension install @jupyter-widgets/jupyterlab-manager

            1. After installation, restart the kernel in all currently running notebooks.

               .. code-block:: shell

                    jupyter labextension list

        * Databricks: Partial support for Juypter Notebook widgets. When you use the widget, it will display a link
          to view the content in a new browser page. Use the :meth:`show` with the ``render_lib`` parameter set to
          'displayHTML'.
    """

    def __new__(cls, run_instance):
        """
        Return a run details widget based on the specified run type.

        :param run_instance: Run instance for which the widget will be rendered.
        :rtype azureml.widgets._widget_run_details_base._WidgetRunDetailsBase
        """
        _run_source_prop = 'azureml.runsource'
        widget_mapper = {
            'hyperdrive': _create_rundetails_importer("hyperdrive", "_HyperDriveRunDetails"),
            'automl': _create_rundetails_importer("automl", "_AutoMLRunDetails"),
            'azureml.PipelineRun': _create_rundetails_importer("pipeline", "_PipelineRunDetails"),
            'azureml.StepRun': _create_rundetails_importer("pipeline", "_StepRunDetails"),
            'reinforcementlearning': _create_rundetails_importer("rl_run", "_RLRunDetails"),
            'experiment': None,
            'azureml.scriptrun': None
        }
        if run_instance.type is None:
            properties = run_instance.get_properties()
            if _run_source_prop in properties:
                run_type = properties[_run_source_prop].lower()
            else:
                run_type = 'experiment'
        else:
            run_type = run_instance.type

        widget_importer = widget_mapper.get(run_type)

        # If no importer is given for the presented type, default to _UserRunDetails
        if widget_importer is not None:
            class_ref = widget_importer()
            assert class_ref
            return class_ref(run_instance)
        else:
            # noinspection PyProtectedMember
            from azureml.widgets._userrun._run_details import _UserRunDetails
            return _UserRunDetails(run_instance)

    def __init__(self, run_instance):
        """
        Initialize widget with provided run instance.

        :param run_instance: Run instance for which the widget will be rendered.
        :type run_instance: azureml.core.run.Run
        """
        pass

    def show(self, render_lib=None, widget_settings=None):
        """
        Render widget and start thread to refresh the widget.

        :param render_lib: The library to use for rendering. Required only for Databricks with value 'displayHTML'.
        :type render_lib: func
        :param widget_settings: Settings to apply to the widget. Supported setting: 'debug' (a boolean).
        :type widget_settings: dict
        """
        pass

    def get_widget_data(self, widget_settings=None):
        """
        Retrieve and transform data from run history to be rendered by widget. Used also for debugging purposes.

        :param widget_settings: Settings to apply to the widget. Supported setting: 'debug' (a boolean).
        :type widget_settings: dict
        :return: Dictionary containing data to be rendered by the widget.
        :rtype: dict
        """
        pass
