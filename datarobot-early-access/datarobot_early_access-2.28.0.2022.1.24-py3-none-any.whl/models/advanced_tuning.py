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
from pprint import pformat
from textwrap import dedent


class NoParametersFoundException(Exception):
    """No parameters were found that matched the specified filter"""

    pass


class NonUniqueParametersException(Exception):
    """Multiple parameters were found that matched the specified filter"""

    def __init__(self, keys, matching_params):
        """Construct a NonUniqueParametersException

        Params
        ------
        keys : dict
            Keys used for filtering
        matching_params : list(dict)
            Parameters that matched the specified filter
        """
        self.matching_params = matching_params

        # Strip non-identifying fields from params for display purposes,
        # to make the error message more concise
        non_identifying_fields = {"defaultValue", "currentValue", "constraints"}
        filtered_params = [
            {key: value for key, value in param.items() if key not in non_identifying_fields}
            for param in matching_params
        ]

        message = dedent(
            """\
            Multiple matching parameters found for the specified keys.
            Keys: {}
            Parameters:
            {}"""
        ).format(pformat(keys), pformat(filtered_params))
        super(NonUniqueParametersException, self).__init__(message)


class AdvancedTuningSession(object):
    """A session enabling users to configure and run advanced tuning for a model.

    Every model contains a set of one or more tasks.  Every task contains a set of
    zero or more parameters.  This class allows tuning the values of each parameter
    on each task of a model, before running that model.

    This session is client-side only and is not persistent.
    Only the final model, constructed when `run` is called, is persisted on the DataRobot server.

    Attributes
    ----------
    description : basestring
        Description for the new advance-tuned model.
        Defaults to the same description as the base model.
    """

    def __init__(self, model):
        """Initiate an Advanced Tuning session.

        Params
        ------
        model : datarobot.models.model.Model
        """
        self._new_values = {}

        self._model = model

        param_info = model.get_advanced_tuning_parameters()
        self._available_params = param_info["tuning_parameters"]
        self.description = param_info.get("tuning_description")

    def _get_parameter_id(self, task_name=None, parameter_name=None, parameter_id=None):
        """Return the ID of the one parameter that matches the specified fields.

        Returns
        -------
        dict
            Parameter dict -- an entry in self._available_params
            (see docstring for `Model.get_advanced_tuning_params`)

        Raises
        ------
        NoParametersFoundException
            if no matching parameters are found.
        NonUniqueParametersException
            if multiple parameters matched the specified filtering criteria
        """
        filtered_params = (x for x in self._available_params)
        if parameter_id:
            # Should be unique but filter normally just in case it's ever not unique
            filtered_params = (x for x in filtered_params if x["parameter_id"] == parameter_id)
        if parameter_name:
            filtered_params = (x for x in filtered_params if x["parameter_name"] == parameter_name)
        if task_name:
            filtered_params = (x for x in filtered_params if x["task_name"] == task_name)

        filtered_params = list(filtered_params)

        if len(filtered_params) == 0:
            raise NoParametersFoundException(
                "No parameters found with task_name of {} and parameter_name of {}".format(
                    repr(task_name) if task_name else "(unspecified)",
                    repr(parameter_name) if parameter_name else "(unspecified)",
                )
            )

        if len(filtered_params) > 1:
            key = {}
            if task_name:
                key["task_name"] = task_name
            if parameter_name:
                key["parameter_name"] = parameter_name
            if parameter_id:
                key["parameter_id"] = parameter_id
            raise NonUniqueParametersException(key, filtered_params)

        return filtered_params[0]["parameter_id"]

    def get_task_names(self):
        """Get the list of task names that are available for this model

        Returns
        -------
        list(basestring)
            List of task names
        """
        return sorted(set(x["task_name"] for x in self._available_params))

    def get_parameter_names(self, task_name):
        """Get the list of parameter names available for a specific task

        Returns
        -------
        list(basestring)
            List of parameter names
        """
        return [x["parameter_name"] for x in self._available_params if x["task_name"] == task_name]

    def set_parameter(self, value, task_name=None, parameter_name=None, parameter_id=None):
        """Set the value of a parameter to be used

        The caller must supply enough of the optional arguments to this function
        to uniquely identify the parameter that is being set.
        For example, a less-common parameter name such as
        'building_block__complementary_error_function' might only be used once (if at all)
        by a single task in a model.  In which case it may be sufficient to simply specify
        'parameter_name'.  But a more-common name such as 'random_seed' might be used by
        several of the model's tasks, and it may be necessary to also specify 'task_name'
        to clarify which task's random seed is to be set.
        This function only affects client-side state. It will not check that the new parameter
        value(s) are valid.

        Parameters
        ----------
        task_name : basestring
            Name of the task whose parameter needs to be set
        parameter_name : basestring
            Name of the parameter to set
        parameter_id : basestring
            ID of the parameter to set
        value : int, float, list, or basestring
            New value for the parameter, with legal values determined by the parameter being set

        Raises
        ------
        NoParametersFoundException
            if no matching parameters are found.
        NonUniqueParametersException
            if multiple parameters matched the specified filtering criteria
        """
        parameter_id = self._get_parameter_id(
            task_name=task_name, parameter_name=parameter_name, parameter_id=parameter_id
        )

        self._new_values[parameter_id] = value

    def _add_value_to_param(self, param):
        """Given a 'param' dict, add a new user-specified value (if any) and return"""
        new_param = dict(param)
        new_param["value"] = self._new_values.get(param["parameter_id"])
        return new_param

    def get_parameters(self):
        """Returns the set of parameters available to this model

        The returned parameters have one additional key, "value", reflecting any new values that
        have been set in this AdvancedTuningSession.  When the session is run, "value" will be used,
        or if it is unset, "current_value".


        Returns
        -------
        parameters : dict
            "Parameters" dictionary, same as specified on `Model.get_advanced_tuning_params`.

        An additional field is added per parameter to the 'tuningParameters' list in the dictionary:

        value : int, float, list, or basestring
            The current value of the parameter.  `None` if none has been specified.
        """

        return {
            "tuning_description": self.description,
            "tuning_parameters": [
                self._add_value_to_param(param) for param in self._available_params
            ],
        }

    def run(self):
        """Submit this model for Advanced Tuning.

        Returns
        -------
        datarobot.models.modeljob.ModelJob
            The created job to build the model
        """
        return self._model.advanced_tune(self._new_values, self.description)
