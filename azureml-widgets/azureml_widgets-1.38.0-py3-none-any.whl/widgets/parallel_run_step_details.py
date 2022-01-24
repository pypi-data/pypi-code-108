# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""ParallelRunStep visualization widget."""
import time

from azureml.core import Run, Workspace

from azureml.widgets._parallel_run_step._parallel_run_step_visualizer import (
    _ParallelRunStepVisualizer,
)


class ParallelRunStepDetails(object):
    """
    Represents a Jupyter notebook widget used to view the progress of ParallelRunStep.

    A widget is synchronous and provides updates until ParallelRunStep finishes.
    """

    def __init__(
        self,
        run_instance: Run = None,
        step_name: str = None,
        workspace: Workspace = None,
        run_id: str = None,
        step_run_id: str = None,
    ):
        """
        Return a ParallelRunStepDetails widget based on the specified run type.
        The ParallelRunStep to be visualized can be specified in either of the following ways:
        * run_instance + step_name
        * workspace + run_id + step_name
        * workspace + step_run_id
        Please make sure one of these combinations is provided in the parameters.
        If multiple ways are provided, the one on top will be chosen.

        :param run_instance: Run instance for which the widget will be rendered.
        :param step_name: Name of the ParallelRunStep in the Run.
        :param workspace: Workspace instance where the Run resides.
        :param run_id: Run id in which the ParallelRunStep resides.
        :param step_run_id: StepRun id for which the widget will be rendered.
        :rtype azureml.widgets.ParallelRunStepDetails
        """
        parameter_name_dict = {
            run_instance: "run_instance",
            step_name: "step_name",
            workspace: "workspace",
            run_id: "run_id",
            step_run_id: "step_run_id",
        }
        expected_parameter_type_dict = {
            run_instance: Run,
            step_name: str,
            workspace: Workspace,
            run_id: str,
            step_run_id: str,
        }
        for parameter, expected_type in expected_parameter_type_dict.items():
            if parameter and not isinstance(parameter, expected_type):
                raise Exception(
                    "{0} must be of type {1}, got {2}".format(
                        parameter_name_dict[parameter], expected_type, type(parameter)
                    )
                )

        not_enough_parameters_message = (
            "The input parameters are not enough to specify a ParallelRunStep, "
            "please make sure ons of the combinations is provided: "
            "(run_instance + step_name) or (workspace + run_id + step_name) or (workspace + step_run_id). "
            "If more than one combinations are provided, the left-most one in the above options will be used."
        )

        if run_instance and step_name:
            self.step_run = self._get_step_run(run_instance, step_name)
        elif workspace and run_id and step_name:
            run_instance = Run.get(workspace, run_id=run_id)
            self.step_run = self._get_step_run(run_instance, step_name)
        elif workspace and step_run_id:
            self.step_run = Run.get(workspace, run_id=step_run_id)
        else:
            raise Exception(not_enough_parameters_message)

    def show(self):
        """Render widget and start synchronous refresh the widget until ParallelRunStep finishes."""
        _ParallelRunStepVisualizer(self.step_run).run()

    def _get_step_run(self, run_instance, step_name, max_try_count=10, try_interval_in_seconds=10):
        """Get StepRun with specified step_name in a Run."""
        step_runs = []
        # At the beginning of the Run, the get_children method returns incomplete result, retry some times.
        try_count = 0
        while try_count < max_try_count:
            children = list(run_instance.get_children())
            step_runs = [r for r in children if r.name == step_name]
            if step_runs:
                break
            try_count += 1
            time.sleep(try_interval_in_seconds)

        if not step_runs:
            raise ValueError("There's no step with the given step_name in the Run.")
        # The StepRuns that matches the step_name, might be plural since step_name is not unique
        if len(step_runs) > 1:
            # TODO: Show as warning
            print(
                "Got multiple step runs that matches the step_name {}, using the first one. "
                "Please set up a unique step name for ParallelRunStep "
                "you want to visualize to avoid this next time.".format(step_name)
            )
        return step_runs[0]
