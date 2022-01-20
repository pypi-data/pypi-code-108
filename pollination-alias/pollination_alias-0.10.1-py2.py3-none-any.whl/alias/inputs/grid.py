from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for text that filters the simulated radiance grids."""
grid_filter_input = [
    InputAlias.str(
        name='grid_filter',
        description='Text for a grid identifier or a pattern to filter the sensor grids '
        'of the model that are simulated. For instance, first_floor_* will simulate '
        'only the sensor grids that have an identifier that starts with '
        'first_floor_. By default, all grids in the model will be simulated.',
        default='*',
        platform=['grasshopper']
    )
]


"""Alias for inputs that split sensor grids for parallel execution."""
sensor_count_input = [
    InputAlias.int(
        name='sensor_count',
        description='Positive integer for the number of sensor grid points per '
        'parallel execution. Lower numbers will result in sensor grids being '
        'split into more pieces and, since each grid piece is run by a separate worker, '
        'this can mean a faster simulation on machines with several CPUs. However ,'
        'If the number is too low, the overhad of splitting the grid will not be worth '
        'the time gained through parallelization. (Default: 200).',
        default=200,
        platform=['grasshopper']
    )
]


"""Alias for inputs that set the minimum number of sensors in split sensor grids."""
min_sensor_count_input = [
    InputAlias.int(
        name='min_sen_count',
        description='Positive integer for the minimum number of sensors in each '
        'grid after redistributing the sensors based on cpu_count. This value takes '
        'precedence over the cpu_count and can be used to ensure that the '
        'parallelization does not result in generating unnecessarily small '
        'sensor grids that increase overhead. (Default: 200).',
        default=200,
        platform=['grasshopper']
    )
]


"""Alias for inputs that set the CPU count by splitting sensor grids."""
cpu_count = [
    InputAlias.int(
        name='cpu_count',
        description='The maximum number of CPUs for parallel execution. For local '
        'simulation, this value is ignored and the cpu_count is automatically set to '
        'be equal to the number of workers tasked to the run. For cloud-based runs, '
        'this input can be used to control the resources used for the simulation and, '
        'if unspecified, the default value of 50 will be used.',
        default=50,
        platform=['grasshopper']
    )
]
