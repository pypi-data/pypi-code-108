from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for inputs that expect an annual schedule as a .csv file."""
schedule_csv_input = [
    InputAlias.any(
        name='schedule',
        description='An annual occupancy schedule, either as a path to a csv file (with '
        '8760 rows), a Ladybug Hourly Continuous Data Collection or a HB-Energy '
        'schedule object. This can also be the identifier of a schedule in '
        'your HB-Energy schedule library. Any value in this schedule that is '
        '0.1 or above will be considered occupied.',
        optional=True,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.schedule',
                function='schedule_to_csv'
            )
        ]
    )
]


"""Alias for inputs that expect a schedule as a .csv file from a data collection."""
comfort_schedule_csv_input = [
    InputAlias.any(
        name='schedule',
        description='A schedule to specify the relevant times during which comfort '
        'should be evaluated. This must either be a Ladybug Hourly Data '
        'Collection that aligns with the input run_period or the path to a '
        'CSV file with a number of rows equal to the length of the run_period. '
        'If unspecified, it will be assumed that all times are relevant for '
        'outdoor sensors and the energy model occupancy schedules will be '
        'used for indoor sensors.',
        optional=True,
        platform=['grasshopper'],
        handler=[
            IOAliasHandler(
                language='python',
                module='pollination_handlers.inputs.schedule',
                function='data_to_csv'
            )
        ]
    )
]
