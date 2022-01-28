from mosaik_scenario_tools.scenario_tools.sink.sink_model import SinkModel

SINK_META: dict = {
    'models': {
        SinkModel.__name__: {
            'public': True,
            'params': [],
            'attrs': [
                'my_attribute',  # input
            ],
        },
    },
}
