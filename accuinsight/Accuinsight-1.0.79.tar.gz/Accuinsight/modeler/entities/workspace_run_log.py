class WorkspaceRunLog:
    """
        Workspace run log parameter object.
    """
    def __init__(self):
        self._workspace_run_id = None
        self._is_success = False
        self._stop_timeout = 60

    def __eq__(self, other):
        if type(other) is type(self):
            # TODO deep equality here?
            return self.__dict__ == other.__dict__
        return False

    @property
    def workspace_run_id(self):
        """Workspace run id."""
        return self._workspace_run_id

    @workspace_run_id.setter
    def workspace_run_id(self, workspace_run_id):
        self._workspace_run_id = workspace_run_id

    @property
    def is_success(self):
        """If the code run succeed."""
        return self._is_success

    @is_success.setter
    def is_success(self, is_success):
        self._is_success = is_success

    @classmethod
    def from_proto(cls, proto):
        pass

    def get_result_param(self):
        """Create and return backend API parameter"""
        import json

        if not self.workspace_run_id:
            raise Exception("workspace_run_id cannot be none")

        data = dict()

        data['workspaceRunId'] = self.workspace_run_id
        data['isSuccess'] = self.is_success

        return json.dumps(data, indent=2)
