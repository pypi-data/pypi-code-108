"""
Base class for parameter-parsing object
"""
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from dkist_processing_common.tasks.mixin.input_dataset import InputDatasetParameterValue


class ParameterBase:
    """
    This class puts all parameters parsed from the input dataset document in a single property on task classes

    There are two main reasons for this:

    1. Segregate the parameters as a .parameters attribute to Science Tasks. This keeps the top-level namespace clean
    2. Allow subclasses to introduce arbitrary logic when parsing instrument-specific parameters (i.e., all of them)

    To use in an instrument pipeline a subclass is required. Here's a simple, but complete example:

        -----
        class InstParameters(ParameterBase)
            def __init__(self, input_dataset_parameters, some_other_parameter):
                super().__init__(input_dataset_parameters)
                self._thing = self._some_function(some_other_parameters)

            @property
            def some_parameter(self):
                return self._find_most_recent_past_value("some_parameter_name")

            @property
            def complicate_parameter(self):
                return self._some_complicated_parsing_function("complicated_parameter_name", another_argument)

        ----

        Note that you can do whatever you want in the definition for each parameter

    Once you have the parameter class it needs to be added to the base Task. This is done by adding/updating
    the instrument's ScienceTask.__init__ function to look similar to this:

            -----
            def __init__(
                self,
                recipe_run_id: int,
                workflow_name: str,
                workflow_version: str,
            ):
                super().__init__(
                    recipe_run_id=recipe_run_id,
                    workflow_name=workflow_name,
                    workflow_version=workflow_version,
                )

                self.parameters = InstParameters(self.input_dataset_parameters)  #<------ This is the important line
            -----

            Note that the first argument to the ConstantsSubclass with *always* be self.input_dataset_parameters, but
            additional argument can be passed if the subclass requires them.

    """

    def __init__(
        self, input_dataset_parameters: Dict[str, List[InputDatasetParameterValue]], **kwargs
    ):
        self.input_dataset_parameters = input_dataset_parameters

    def _find_most_recent_past_value(
        self,
        parameter_name: str,
        start_date: Optional[datetime] = None,
    ) -> Any:
        """ Get a single value from the input_dataset_parameters """
        start_date = start_date or datetime.utcnow()
        values = self.input_dataset_parameters[parameter_name]  # Force KeyError if it doesn't exist
        sorted_values_from_before = sorted(
            [v for v in values if v.parameter_value_start_date <= start_date],
            key=lambda x: x.parameter_value_start_date,
        )
        try:
            result = sorted_values_from_before.pop().parameter_value
        except IndexError:
            raise ValueError(
                f"{parameter_name} has no values before {start_date.isoformat()} ({len(values)} values in total)"
            )
        return result
