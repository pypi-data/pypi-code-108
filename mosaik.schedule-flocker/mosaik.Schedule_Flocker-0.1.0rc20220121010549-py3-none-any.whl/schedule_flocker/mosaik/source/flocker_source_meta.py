from mosaik_schedule_flocker.schedule_flocker.mosaik.source.\
    flocker_source_model import FlockerSourceModel

FLOCKER_SOURCE_META: dict = {
    'models': {
        FlockerSourceModel.__name__: {
            'public': True,
            'params': [
            ],
            'attrs': [
                'config',  # output
            ],
        },
    },
}
