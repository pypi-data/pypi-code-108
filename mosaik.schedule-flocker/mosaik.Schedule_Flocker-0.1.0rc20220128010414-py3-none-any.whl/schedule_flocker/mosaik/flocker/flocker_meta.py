from mosaik_schedule_flocker.schedule_flocker.mosaik.flocker.flocker_model \
    import FlockerModel

FLOCKER_META: dict = {
    'models': {
        FlockerModel.__name__: {
            'public': True,
            'params': [
            ],
            'attrs': [
                'config',  # input
                'flexibility_schedules',  # output
            ],
        },
    },
}
