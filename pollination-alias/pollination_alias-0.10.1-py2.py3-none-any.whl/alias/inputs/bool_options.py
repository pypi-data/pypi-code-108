from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for yes/no inputs about whether to filter design days."""
filter_des_days_input = [
    InputAlias.any(
        name='filter_des_days',
        description='A boolean to note whether the ddy file should be filtered to only '
        'include 99.6 and 0.4 design days (True) or all design days in the ddy file '
        'should be used (False).',
        default=True,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.bool_options',
                function='filter_des_days_to_str'
            )
        ]
    )
]


"""Alias for yes/no inputs about whether to skip a view-based overture calculation."""
skip_overture_input = [
    InputAlias.any(
        name='skip_overture',
        description='A boolean to note whether an ambient file (.amb) should be '
        'generated for an overture calculation before the view is split into smaller '
        'views. With an overture calculation, the ambient file (aka ambient cache) is '
        'first populated with values. Thereby ensuring that - when reused to create '
        'an image - Radiance uses interpolation between already calculated values '
        'rather than less reliable extrapolation. The overture calculation has '
        'comparatively small computation time to full rendering but is single-core '
        'can become time consuming in situations with very high numbers of '
        'rendering multiprocessors.',
        default=False,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.bool_options',
                function='skip_overture_to_str'
            )
        ]
    )
]


"""Alias for yes/no inputs about whether glare control devices exist in a model."""
glare_control_devices_input = [
    InputAlias.any(
        name='glare_control',
        description='A boolean to note whether the model has "view-preserving automatic '
        '(with manual override) glare-control devices," which means that illuminance '
        'only needs to be above 300 lux and not between 300 and 3000 lux.',
        default=True,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.bool_options',
                function='glare_control_devices_to_str'
            )
        ]
    )
]


"""Alias for yes/no inputs about whether to use multipliers."""
use_multiplier_input = [
    InputAlias.any(
        name='use_multiplier',
        description='If True, the multipliers on each Building Stories will be '
        'passed along to the generated Honeybee Room objects, indicating the '
        'simulation will be run once for each unique room and then results '
        'will be multiplied. If False, full geometry objects will be written '
        'for each and every story in the building such that all resulting '
        'multipliers will be 1. (Default: False).',
        default=False,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.bool_options',
                function='use_multiplier_to_str'
            )
        ]
    )
]


"""Alias for yes/no inputs about whether a building is residential."""
is_residential_input = [
    InputAlias.any(
        name='is_residential',
        description='A boolean to note whether the model represents a residential '
        'or nonresidential building.',
        default=False,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.bool_options',
                function='is_residential_to_str'
            )
        ]
    )
]


"""Alias for yes/no inputs about whether a comfort map should be for SET."""
write_set_map_input = [
    InputAlias.any(
        name='write_set_map',
        description='A boolean to note whether the output temperature CSV should '
        'record Operative Temperature or Standard Effective Temperature (SET). '
        'SET is relatively intense to compute and so only recording Operative '
        'Temperature can greatly reduce run time, particularly when air speeds '
        'are low. However, SET accounts for all 6 PMV model inputs and so is a '
        'more representative "feels-like" temperature for the PMV model.',
        default=False,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.bool_options',
                function='write_set_map_to_str'
            )
        ]
    )
]


"""Alias for yes/no inputs about whether to compute sky view or sky exposure."""
sky_exposure_input = [
    InputAlias.any(
        name='exposure',
        description='A boolean to note whether the output values should be sky view '
        '(False) or sky exposure (True). Sky View is defined as the percent of the '
        'sky dome seen by a surface and Sky Exposure is the fraction of the sky '
        'dome seen by a point. (Default: False)',
        default=False,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.bool_options',
                function='sky_view_metric_to_str'
            )
        ]
    )
]


"""Alias for yes/no inputs about whether to use a cloudy or uniform sky."""
cloudy_uniform_input = [
    InputAlias.any(
        name='cloudy_sky',
        description='A boolean to note whether a uniform sky should be used  '
        '(False) or a cloudy overcast sky (True). (Default: False).',
        default=False,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.bool_options',
                function='cloudy_bool_to_str'
            )
        ]
    )
]
