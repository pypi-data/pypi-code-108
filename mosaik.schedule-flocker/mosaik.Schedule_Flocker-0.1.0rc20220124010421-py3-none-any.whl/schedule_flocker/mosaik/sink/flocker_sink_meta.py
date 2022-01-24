from mosaik_schedule_flocker.schedule_flocker.mosaik.sink.flocker_sink_model \
    import FlockerSinkModel

FLOCKER_SINK_META: dict = {
    'models': {
        FlockerSinkModel.__name__: {
            'public': True,
            'params': [
            ],
            'attrs': [
                'flexibility_schedules',  # input
            ],
        },
    },
}
