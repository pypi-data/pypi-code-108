from rox.core.impression.models.reporting_value import ReportingValue
from rox.server.flags.flag_types import FlagTypes


class RoxBase(object):
    def __init__(self, default_value, options = [], rox_type=FlagTypes.STRING):
        if default_value is None:
            raise TypeError('Default value can\'t be None')
        options = list(options)
        if default_value not in options:
            options.append(default_value)

        self.options = options
        self.default_value = default_value

        self.condition = None
        self.parser = None
        self.impression_invoker = None
        self.experiment = None
        self.name = None
        self.rox_type = rox_type
        self.validate()

    def set_for_evaluation(self, parser, impression_invoker, experiment=None):
        if experiment is not None:
            self.experiment = experiment
            self.condition = experiment.condition
        else:
            self.experiment = None
            self.condition = ''

        self.parser = parser
        self.impression_invoker = impression_invoker

    def set_name(self, name):
        self.name = name

    def _get_value(self, context, none_instead_of_default=None):
        return_value = None if none_instead_of_default else self.default_value

        if self.parser is not None and self.condition:
            evaluation_result = self.parser.evaluate_expression(self.condition, context=context)
            if evaluation_result is not None:
                if self.rox_type is FlagTypes.STRING:
                    value = evaluation_result.string_value()
                else:
                    value = evaluation_result.value
                if value is not None:
                    return_value = value

        return return_value

    def send_impressions(self, value, merged_context):
        if self.impression_invoker is not None:
            self.impression_invoker.invoke(ReportingValue(self.name, value, self.experiment != None), None if self.experiment is None else self.experiment.stickinessProperty, merged_context)

    def validate(self):
        try:
            self.rox_type(self.default_value)
        except ValueError:
            raise ValueError('{} is not of type {}'.format(self.default_value, self.rox_type))
        for option in self.options:
            try:
                self.rox_type(option)
            except ValueError:
                raise ValueError('{} is not of type {}'.format(option, self.rox_type))


    def __repr__(self):
        return "%s(%r, %r)" % (type(self).__name__, self.default_value, self.options)

    def __str__(self):
        return "%s(%s, %s, name=%s, condition=%s)" % (type(self).__name__, self.default_value, self.options, self.name, self.condition)
