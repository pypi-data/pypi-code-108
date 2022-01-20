from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for the selection of point-in-time metrics."""
point_in_time_metric_input = [
    InputAlias.any(
        name='metric',
        description='Either an integer or the full name of a point-in-time metric to '
        'be computed by the recipe. (Default: illuminance). Choose from the following:'
        '\n* 0 = illuminance\n* 1 = irradiance\n* 2 = luminance\n* 3 = radiance',
        default='illuminance',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.pit',
                function='point_in_time_metric_to_str'
            )
        ]
    )
]


"""Alias for the selection of point-in-time metrics."""
point_in_time_view_metric_input = [
    InputAlias.any(
        name='metric',
        description='Either an integer or the full name of a point-in-time metric to '
        'be computed by the recipe. (Default: luminance). Choose from the following:'
        '\n* 0 = illuminance\n* 1 = irradiance\n* 2 = luminance\n* 3 = radiance',
        default='luminance',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.pit',
                function='point_in_time_metric_to_str'
            )
        ]
    )
]
