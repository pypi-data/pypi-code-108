from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias inputs that expect a HBJSON model file as the recipe input."""
hbjson_model_input = [
    # grasshopper Alias
    InputAlias.any(
        name='model',
        description='A Honeybee Model to simulate or the path to a HBJSON file '
        'of a Model. This can also be the path to a HBpkl file, though this is only '
        'recommended for cases where the model is extremely large.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python', module='pollination_handlers.inputs.model',
                function='model_to_json'
            ),
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='HBModelToJSON'
            )
        ]
    ),
    # Rhino alias
    InputAlias.linked(
        name='model',
        description='This input links the model to Rhino model.',
        platform=['rhino'],
        handler=[
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='RhinoHBModelToJSON'
            )
        ]
    )
]


"""Alias inputs that expect a HBJSON model with sensor grids."""
hbjson_model_grid_input = [
    # grasshopper Alias
    InputAlias.any(
        name='model',
        description='A Honeybee Model to simulate or the path to a HBJSON file '
        'of a Model. This can also be the path to a HBpkl file, though this is only '
        'recommended for cases where the model is extremely large. Note that this '
        'model should have sensor grids assigned to it.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python', module='pollination_handlers.inputs.model',
                function='model_to_json_grid_check'
            ),
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='HBModelToJSON'
            )
        ]
    ),
    # Rhino alias
    InputAlias.linked(
        name='model',
        description='This input links the model to Rhino model.',
        platform=['rhino'],
        handler=[
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='RhinoHBModelToJSON'
            )
        ]
    )
]


"""Alias inputs that expect a HBJSON model with sensor grids and rooms."""
hbjson_model_grid_room_input = [
    # grasshopper Alias
    InputAlias.any(
        name='model',
        description='A Honeybee Model to simulate or the path to a HBJSON file '
        'of a Model. Note that this model must contain rooms and have sensor '
        'grids assigned to it.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python', module='pollination_handlers.inputs.model',
                function='model_to_json_grid_room_check'
            ),
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='HBModelToJSON'
            )
        ]
    ),
    # Rhino alias
    InputAlias.linked(
        name='model',
        description='This input links the model to Rhino model.',
        platform=['rhino'],
        handler=[
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='RhinoHBModelToJSON'
            )
        ]
    )
]


"""Alias inputs that expect a HBJSON model with views."""
hbjson_model_view_input = [
    # grasshopper Alias
    InputAlias.any(
        name='model',
        description='A Honeybee Model to simulate or the path to a HBJSON file '
        'of a Model. This can also be the path to a HBpkl file, though this is only '
        'recommended for cases where the model is extremely large. Note that this '
        'model should have views assigned to it.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python', module='pollination_handlers.inputs.model',
                function='model_to_json_view_check'
            ),
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='HBModelToJSON'
            )
        ]
    ),
    # Rhino alias
    InputAlias.linked(
        name='model',
        description='This input links the model to Rhino model.',
        platform=['rhino'],
        handler=[
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='RhinoHBModelToJSON'
            )
        ]
    )
]


"""Alias inputs that expect a HBJSON model with views."""
hbjson_model_view_input = [
    # grasshopper Alias
    InputAlias.any(
        name='model',
        description='A Honeybee Model to simulate or the path to a HBJSON file '
        'of a Model. This can also be the path to a HBpkl file, though this is only '
        'recommended for cases where the model is extremely large. Note that this '
        'model should have views assigned to it.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python', module='pollination_handlers.inputs.model',
                function='model_to_json_view_check'
            ),
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='HBModelToJSON'
            )
        ]
    ),
    # Rhino alias
    InputAlias.linked(
        name='model',
        description='This input links the model to Rhino model.',
        platform=['rhino'],
        handler=[
            IOAliasHandler(
                language='csharp', module='Pollination.RhinoHandlers',
                function='RhinoHBModelToJSON'
            )
        ]
    )
]

"""Alias inputs that expect a DFJSON model file as the recipe input."""
dfjson_model_input = [
    # grasshopper Alias
    InputAlias.any(
        name='model',
        description='A Dragonfly Model object or the path to a DFJSON file.',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python', module='pollination_handlers.inputs.model',
                function='model_dragonfly_to_json'
            )
        ]
    )
]
