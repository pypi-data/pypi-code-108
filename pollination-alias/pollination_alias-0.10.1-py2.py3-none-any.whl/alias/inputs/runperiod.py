from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for simulation run periods."""
run_period_input = [
    InputAlias.str(
        name='run_period',
        description='An AnalysisPeriod to set the start and end dates of the '
        'simulation. If None, the simulation will be annual.',
        default='',
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.runperiod',
                function='run_period_to_str'
            )
        ]
    )
]
