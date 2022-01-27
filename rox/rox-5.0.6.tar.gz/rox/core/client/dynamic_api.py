from rox.core.entities.flag import Flag
from rox.server.flags.flag_types import FlagTypes
from rox.server.flags.normalize_flag_type import NormalizeFlagType
from rox.core.context.merged_context import MergedContext


class DynamicApi:
    def __init__(self, flag_repository, entities_provider):
        self.flag_repository = flag_repository
        self.entities_provider = entities_provider

    def is_enabled(self, name, default_value, context=None):
        variant = self.flag_repository.get_flag(name)
        if variant is None:
            variant = self.entities_provider.create_flag(default_value)
            self.flag_repository.add_flag(variant, name)

        merged_context = MergedContext(variant.parser.global_context if variant.parser is not None else None, context)
        is_enabled = variant._is_enabled(context, none_instead_of_default=True)
        return_value = is_enabled if is_enabled is not None else default_value
        variant.send_impressions(return_value, merged_context)
        return return_value

    def value(self, name, default_value, options=[], context=None):
        return self._generic_value(name, default_value, options, context)

    def get_int(self, name, default_value, options=[], context=None):
        return self._generic_value(name, default_value, options, context, self.entities_provider.create_int, NormalizeFlagType.normalize_int)

    def get_double(self, name, default_value, options=[], context=None):
        return self._generic_value(name, default_value, options, context, self.entities_provider.create_double, NormalizeFlagType.normalize_float)

    def _generic_value(self, name, default_value, options, context, create_method = None, normalize_method = NormalizeFlagType.normalize_string):
        if default_value is None:
            raise TypeError('Default value cannot be None')

        if type(name) is not str:
            raise TypeError('DynamicApi error - name must be string')

        if create_method is None:
            create_method = self.entities_provider.create_string

        variant = self.flag_repository.get_flag(name)
        if variant is None:
            variant = create_method(default_value, options)
            self.flag_repository.add_flag(variant, name)

        merged_context = MergedContext(variant.parser.global_context if variant.parser is not None else None, context)
        value = variant._get_value(merged_context, none_instead_of_default=True)
        return_value = normalize_method(value) if value is not None else normalize_method(default_value)
        variant.send_impressions(return_value, merged_context)
        return return_value