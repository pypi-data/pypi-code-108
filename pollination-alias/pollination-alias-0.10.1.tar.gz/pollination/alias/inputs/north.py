from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for north inputs that can accept both an angle or a north vector."""
north_input = [
    InputAlias.any(
        name='north',
        description='A number between -360 and 360 for the counterclockwise difference '
        'between the North and the positive Y-axis in degrees. This can '
        'also be Vector for the direction to North. (Default: 0).',
        default=0,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.north',
                function='north_vector_to_angle'
            )
        ]
    )
]
