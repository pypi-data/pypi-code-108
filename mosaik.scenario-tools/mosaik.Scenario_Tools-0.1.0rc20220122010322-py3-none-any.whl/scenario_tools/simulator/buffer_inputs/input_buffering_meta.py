from mosaik_scenario_tools.scenario_tools.simulator.buffer_inputs.\
    input_buffering_simulator import InputBufferingSimulator

INPUT_BUFFERING_META: dict = {
    'models': {
        InputBufferingSimulator.__name__: {
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
