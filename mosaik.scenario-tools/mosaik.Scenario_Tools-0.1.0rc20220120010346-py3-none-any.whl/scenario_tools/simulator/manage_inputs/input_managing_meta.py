from mosaik_scenario_tools.scenario_tools.simulator.manage_inputs.\
    input_managing_simulator import \
    InputManagingSimulator

INPUT_MANAGING_META: dict = {
    'models': {
        InputManagingSimulator.__name__: {
            'public': True,
            'params': [
            ],
            'attrs': [
                'x',
                'y',
            ],
        },
    },
}
