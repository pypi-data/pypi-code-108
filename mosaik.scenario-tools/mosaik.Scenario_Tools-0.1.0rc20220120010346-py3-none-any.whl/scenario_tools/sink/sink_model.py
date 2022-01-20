class SinkModel(object):
    def __init__(self, eid):
        """
        This is the simplest-thinkable source model

        :param eid: The entity identifier this model shall carry
        """

        self._eid = eid
        self._data = None

    @property
    def eid(self):
        return self._eid

    def get_data(self):
        return self._data

    def step(self, input):
        # Sink the input.
        del input

        self._data = None
