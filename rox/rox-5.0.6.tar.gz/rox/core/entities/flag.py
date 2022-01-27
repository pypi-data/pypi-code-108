from rox.core.entities.rox_base import RoxBase
from rox.server.flags.flag_types import FlagTypes
from rox.core.context.merged_context import MergedContext
from rox.core.entities.default_flag_values import DefaultFlagValues


class Flag(RoxBase):
    FLAG_TRUE_VALUE = 'true'
    FLAG_FALSE_VALUE = 'false'

    def __init__(self, default_value=DefaultFlagValues.BOOLEAN):
        super(Flag, self).__init__(Flag.FLAG_TRUE_VALUE if default_value else Flag.FLAG_FALSE_VALUE, [Flag.FLAG_FALSE_VALUE, Flag.FLAG_TRUE_VALUE])

    def is_enabled(self, context=None):
        merged_context = MergedContext(self.parser.global_context if self.parser is not None else None, context)
        value = self._is_enabled(merged_context)
        if isinstance(value, FlagTypes.BOOLEAN):
            self.send_impressions(value, merged_context)
            return value
        self.send_impressions(DefaultFlagValues.BOOLEAN, merged_context)
        return DefaultFlagValues.BOOLEAN

    def _is_enabled(self, context, none_instead_of_default=False):
        value = self._get_value(context, none_instead_of_default)
        return None if none_instead_of_default and value is None else self.is_enabled_from_string(value)

    def enabled(self, context, action):
        if self.is_enabled(context):
            action()

    def disabled(self, context, action):
        if not self.is_enabled(context):
            action()

    def is_enabled_from_string(self, value):
        return value == Flag.FLAG_TRUE_VALUE

    def get_value(self, context=None):
        merged_context = MergedContext(self.parser.global_context if self.parser is not None else None, context)
        value = self._get_value(merged_context)
        self.send_impressions(value, merged_context)
        return value

    def __repr__(self):
        return "%s(%r)" % (type(self).__name__, True if self.default_value == Flag.FLAG_TRUE_VALUE else False)

    def __str__(self):
        return "%s(%s, name=%s, condition=%s)" % (type(self).__name__, True if self.default_value == Flag.FLAG_TRUE_VALUE else False, self.name, self.condition)
