from mosaik_schedule_flocker.schedule_flocker.data.\
    get_mock_flocker_config_module import get_mock_flocker_config


class FlockerSourceModel(object):
    def __init__(self, *,
                 eid):
        self._eid = eid

    @property
    def eid(self):
        return self._eid

    def get_data(self):
        # generate multiple configs for multiple units
        flocker_configs = []

        for idx in range(6):
            flocker_configs.append(get_mock_flocker_config(idx))

        data = {
            'config': flocker_configs,
        }

        return data
