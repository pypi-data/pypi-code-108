from pollination_dsl.alias import OutputAlias
from queenbee.io.common import IOAliasHandler


"""Annual energy use recipe output.

The result is a JSON with various end uses of energy.
"""
parse_eui_results = [
    OutputAlias.any(
        name='eui',
        description='Energy Use intensity, including total and for each end use.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.outputs.eui',
                function='eui_json_from_path'
            )
        ]
    )
]
