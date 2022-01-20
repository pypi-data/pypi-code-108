from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for inputs that expect a .ddy file as the recipe input."""
ddy_input = [
    InputAlias.any(
        name='ddy',
        description='The path to a .ddy file or an .epw file with design days to be '
        'used for the initial sizing calculation.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.ddy',
                function='ddy_handler'
            )
        ]
    )
]
