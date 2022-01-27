import math

from rox.core.entities.flag import Flag

class InternalFlags:
    defaults_self_managed = {
        "rox.internal.pushUpdates": False,
        "rox.internal.considerThrottleInPush": False,
        "rox.internal.throttleFetchInSeconds": 0
    }

    def __init__(self, experiment_repository, parser, rox_options):
        self.experiment_repository = experiment_repository
        self.parser = parser
        self.rox_options = rox_options

    def get_default_value(self, flag_name):
        if not self.rox_options.is_self_managed() or flag_name not in self.defaults_self_managed:
            return None

        return self.defaults_self_managed[flag_name]


    def is_enabled(self, flag_name):
        default_value = self.get_default_value(flag_name)
        if default_value is not None and type(default_value) is type(True):
            return default_value

        internal_experiment = self.experiment_repository.get_experiment_by_flag(flag_name)
        if internal_experiment is None:
            return False

        value = self.parser.evaluate_expression(internal_experiment.condition, None).string_value()
        return value == Flag.FLAG_TRUE_VALUE

    def get_number_value(self, flag_name):
        default_value = self.get_default_value(flag_name)
        if default_value is not None:
            return default_value

        internal_experiment = self.experiment_repository.get_experiment_by_flag(flag_name)
        if internal_experiment is None:
            return None

        value = self.parser.evaluate_expression(internal_experiment.condition, None).string_value()
        try:
            number = float(value)
            if math.isnan(number):
                return None
            return number
        except ValueError:
            return None
