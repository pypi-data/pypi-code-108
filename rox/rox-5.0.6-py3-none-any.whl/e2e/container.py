from rox.server.flags.rox_flag import RoxFlag
from rox.server.flags.rox_string import RoxString
from rox.server.flags.rox_int import RoxInt
from rox.server.flags.rox_double import RoxDouble


class Container:
    instance = None

    def __init__(self):
        self.simple_flag = RoxFlag(True)
        self.simple_flag_overwritten = RoxFlag(True)

        self.flag_for_impression = RoxFlag(False)
        self.flag_for_impression_with_experiment_and_context = RoxFlag(False)

        self.flag_custom_properties = RoxFlag()

        self.flag_target_groups_all = RoxFlag()
        self.flag_target_groups_any = RoxFlag()
        self.flag_target_groups_none = RoxFlag()

        self.variant_with_context = RoxString('red', ['red', 'blue', 'green'])

        self.variant = RoxString('red', ['red', 'blue', 'green'])
        self.size_variant = RoxInt(14, [14, 24, 40])
        self.specific_size_variant = RoxDouble(14.4, [14.4, 24.0, 40.7])

        self.variant_overwritten = RoxString('red', ['red', 'blue', 'green'])
        self.size_variant_overwritten = RoxInt(14, [14, 24, 40])
        self.specific_size_variant_overwritten = RoxDouble(14.4, [14.4, 24.0, 40.7])

        self.flag_for_dependency = RoxFlag(False)
        self.flag_colors_for_dependency = RoxString('White', ['White', 'Blue', 'Green', 'Yellow'])
        self.flag_dependent = RoxFlag(False)
        self.flag_color_dependent_with_context = RoxString('White', ['White', 'Blue', 'Green', 'Yellow'])


Container.instance = Container()
