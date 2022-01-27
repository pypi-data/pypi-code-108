class DeployLog:
    """
        Deploy log parameter object.
    """

    def __init__(self):
        self.run_id = None
        self._response_data = None

    def __eq__(self, other):
        if type(other) is type(self):
            # TODO deep equality here?
            return self.__dict__ == other.__dict__
        return False

    @property
    def run_id(self):
        """String the deploy api response."""
        return self._run_id

    @run_id.setter
    def run_id(self, run_id):
        self._run_id = run_id

    @property
    def response_data(self):
        """String the deploy api response."""
        return self._response_data

    @response_data.setter
    def response_data(self, response_data):
        self._response_data = response_data

    @classmethod
    def from_proto(cls, proto):
        pass

    def get_logging_param(self):
        """Create and return backend API parameter"""
        import json

        if self.run_id is None:
            raise Exception("run_id cannot be None")

        if self.response_data is None:
            raise Exception("response_data cannot be None")

        data = dict()
        data['run_id'] = self.run_id
        data['response'] = self.response_data

        return json.dumps(data, indent=2)
