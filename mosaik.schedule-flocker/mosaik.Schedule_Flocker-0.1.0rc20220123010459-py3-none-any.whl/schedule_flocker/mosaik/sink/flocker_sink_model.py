class FlockerSinkModel(object):
    def __init__(self, eid):
        self.eid = eid

    def step(self, inputs):
        print('sink inputs type:', type(inputs))
        assert type(inputs) is dict
        print('sink inputs keys:', inputs.keys())
        assert 'flexibility_schedules' in inputs.keys()

        print(
            'sink inputs["flexibility_schedules"] type:',
            type(inputs["flexibility_schedules"])
        )
        print(
            'sink inputs["flexibility_schedules"] keys:',
            inputs["flexibility_schedules"].keys()
        )
        print(
            'sink inputs["flexibility_schedules"]["FlockerSimulator-0.FlockerModel-0"] '
            'type:',
            type(inputs["flexibility_schedules"]["FlockerSimulator-0.FlockerModel-0"])
        )
        print(
            'sink inputs["flexibility_schedules"]["FlockerSimulator-0.FlockerModel-0"] '
            'length:',
            len(inputs["flexibility_schedules"]["FlockerSimulator-0.FlockerModel-0"])
        )
        print(
            'sink inputs["flexibility_schedules"]["FlockerSimulator-0.FlockerModel-0"][0] '
            'type:',
            type(inputs["flexibility_schedules"][
                     "FlockerSimulator-0.FlockerModel-0"][0])
        )
        print(
            'sink inputs["flexibility_schedules"]["FlockerSimulator-0.FlockerModel-0"][0] '
            'length:',
            len(inputs["flexibility_schedules"][
                "FlockerSimulator-0.FlockerModel-0"][0])
        )
        print(
            'sink inputs["flexibility_schedules"]["FlockerSimulator-0.FlockerModel-0"][1] '
            'type:',
            type(inputs["flexibility_schedules"][
                     "FlockerSimulator-0.FlockerModel-0"][1])
        )
        print(
            'sink inputs["flexibility_schedules"]["FlockerSimulator-0.FlockerModel-0"][1] '
            'length:',
            len(inputs["flexibility_schedules"][
                "FlockerSimulator-0.FlockerModel-0"][1])
        )
