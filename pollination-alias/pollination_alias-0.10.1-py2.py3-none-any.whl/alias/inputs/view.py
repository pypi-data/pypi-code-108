from pollination_dsl.alias import InputAlias
from queenbee.io.common import IOAliasHandler


"""Alias for inputs that set the CPU count by splitting views."""
cpu_count = [
    InputAlias.int(
        name='cpu_count',
        description='The maximum number of CPUs for parallel execution. For local '
        'simulation, this value is ignored and the cpu_count is automatically set to '
        'be equal to the number of workers tasked to the run. For cloud-based runs, '
        'this input can be used to control the resources used for the simulation and, '
        'if unspecified, the default value of 12 will be used.',
        default=12,
        platform=['grasshopper']
    )
]
