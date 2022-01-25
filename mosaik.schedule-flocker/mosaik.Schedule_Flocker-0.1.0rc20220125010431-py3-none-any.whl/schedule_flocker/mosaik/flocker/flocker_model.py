from mosaik_schedule_flocker.schedule_flocker.core.generator import \
    Generator


class FlockerModel(object):
    def __init__(self, *,
                 eid):
        # Entity Identifier
        self.eid = eid

        # Persistent generator instance
        self.generator = Generator()

        # Cached generated schedule flock
        self._flock = []

    def get_data(self):
        return {'flexibility_schedules': self._flock}

    def step(self, *,
             inputs):
        for config in inputs:
            self._flock.extend(
                self.generator.generate_schedule_flock_by_objects(
                    config=config
                ))
