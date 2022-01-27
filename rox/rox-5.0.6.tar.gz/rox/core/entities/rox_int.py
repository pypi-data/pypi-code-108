from rox.core.entities.rox_base import RoxBase
from rox.server.flags.flag_types import FlagTypes
from rox.core.context.merged_context import MergedContext
from rox.core.entities.default_flag_values import DefaultFlagValues


class RoxInt(RoxBase):
    def __init__(self, default_value=DefaultFlagValues.INT, options = []):
        super(RoxInt, self).__init__(default_value, options, FlagTypes.INT)

    def get_value(self, context=None):
        return self.get_int(context)

    def get_int(self, context=None):
        merged_context = MergedContext(self.parser.global_context if self.parser is not None else None, context)
        value = self._get_value(merged_context, none_instead_of_default=False)
        if isinstance(value, FlagTypes.INT):
            self.send_impressions(value, merged_context)
            return value
        self.send_impressions(DefaultFlagValues.INT, merged_context)
        return DefaultFlagValues.INT
        