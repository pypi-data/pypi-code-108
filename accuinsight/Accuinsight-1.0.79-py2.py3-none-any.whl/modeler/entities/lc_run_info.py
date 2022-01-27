from Accuinsight.modeler.entities._modeler_object import _ModelerObject


class LcRunInfo(_ModelerObject):
    """
    Metadata about a run.
    """

    def __init__(self,
                 user_id,
                 start_time,
                 end_time,
                 duration,
                 artifact_location,
                 run_status,
                 path,
                 model_path,
                 json_path,
                 run_name=None,
                 note=None):
        if user_id is None:
            raise Exception("user_id cannot be None")
        if start_time is None:
            raise Exception("start_time cannot be None")
        if end_time is None:
            raise Exception("end_time cannot be None")
        if duration is None:
            raise Exception("duration cannot be None")
        if artifact_location is None:
            raise Exception("duratiartifact_locationn cannot be None")
        if run_status is None:
            raise Exception("run_status cannot be None")
        if path is None:
            raise Exception("notebook_path cannot be None")
        if model_path is None:
            raise Exception("model file path cannot be None")
        if json_path is None:
            raise Exception("model json file path cannot be None")

        self._run_name = run_name
        self._user_id = user_id
        self._start_time = start_time
        self._end_time = end_time
        self._duration = duration
        self._artifact_location = artifact_location
        self._run_status = run_status
        self._note = note
        self._path = path
        self._model_path = model_path
        self._json_path = json_path

    def __eq__(self, other):
        if type(other) is type(self):
            # TODO deep equality here?
            return self.__dict__ == other.__dict__
        return False

    @property
    def run_name(self):
        """String the name of run."""
        return self._run_name

    @property
    def user_id(self):
        """String ID of the user who initiated this run."""
        return self._user_id

    @property
    def start_time(self):
        """Start time of the run, in number of milliseconds since the UNIX epoch."""
        return self._start_time

    @property
    def end_time(self):
        """End time of the run, in number of milliseconds since the UNIX epoch."""
        return self._end_time

    @property
    def duration(self):
        """The total elapsed time of the run, in number of milliseconds since the UNIX epoch."""
        return self._duration

    @property
    def artifact_location(self):
        """The artifact location for the current run."""
        return self._artifact_location

    @property
    def run_status(self):
        """
        One of the values in /entities/lc_run_status.py
        describing the status of the run.
        """
        return self._run_status

    @property
    def note(self):
        """
        The extra information for the current run.
        This value is set by user.
        """
        return self._note

    @property
    def path(self):
        """
        the name of current selected notebook.
        """
        return self._path

    @property
    def model_path(self):
        """
        the path of model file.
        """
        return self._model_path

    @property
    def json_path(self):
        """
        the path of model json file.
        """
        return self._json_path

    def to_proto(self):
        proto = ProtoLcRunInfo()
        proto.name = self.run_name
        proto.userId = self.user_id
        proto.creaDt = self.start_time
        proto.endDt = self.end_time
        proto.duration = self.duration
        proto.afLoc = self.artifact_location
        proto.status = RunStatus.from_string(self.run_status)
        proto.note = self.note
        proto.path = self._path
        proto.modelPath = self._model_path
        proto.jsonPath = self._json_path
        return proto

    @classmethod
    def from_proto(cls, proto):
        end_time = proto.endDt
        # The proto2 default scalar value of zero indicates that the run's end time is absent.
        # An absent end time is represented with a NoneType in the `RunInfo` class
        if end_time == 0:
            end_time = None
        return cls(user_id=proto.userId,
                   start_time=proto.creaDt,
                   end_time=proto.endDt,
                   duration=proto.duration,
                   artifact_location=proto.afLoc,
                   run_status=proto.status,
                   model_path=proto.modelPath,
                   json_path=proto.jsonPath,
                   run_name=proto.name,
                   note=proto.note)
from Accuinsight.modeler.entities.lc_run_status import RunStatus
from Accuinsight.modeler.entities._modeler_object import _ModelerObject
from Accuinsight.modeler.protos.life_cycle_pb2 import LcRunInfo as ProtoLcRunInfo


class LcRunInfo(_ModelerObject):
    """
    Metadata about a run.
    """

    def __init__(self,
                 user_id,
                 start_time,
                 end_time,
                 duration,
                 artifact_location,
                 run_status,
                 path,
                 model_path,
                 json_path,
                 run_name=None,
                 note=None):
        if user_id is None:
            raise Exception("user_id cannot be None")
        if start_time is None:
            raise Exception("start_time cannot be None")
        if end_time is None:
            raise Exception("end_time cannot be None")
        if duration is None:
            raise Exception("duration cannot be None")
        if artifact_location is None:
            raise Exception("duratiartifact_locationn cannot be None")
        if run_status is None:
            raise Exception("run_status cannot be None")
        if path is None:
            raise Exception("notebook_path cannot be None")
        if model_path is None:
            raise Exception("model file path cannot be None")
        if json_path is None:
            raise Exception("model json file path cannot be None")
        
        self._run_name = run_name
        self._user_id = user_id
        self._start_time = start_time
        self._end_time = end_time
        self._duration = duration
        self._artifact_location = artifact_location
        self._run_status = run_status
        self._note = note
        self._path = path
        self._model_path = model_path
        self._json_path = json_path

    def __eq__(self, other):
        if type(other) is type(self):
            # TODO deep equality here?
            return self.__dict__ == other.__dict__
        return False

    @property
    def run_name(self):
        """String the name of run."""
        return self._run_name

    @property
    def user_id(self):
        """String ID of the user who initiated this run."""
        return self._user_id

    @property
    def start_time(self):
        """Start time of the run, in number of milliseconds since the UNIX epoch."""
        return self._start_time

    @property
    def end_time(self):
        """End time of the run, in number of milliseconds since the UNIX epoch."""
        return self._end_time

    @property
    def duration(self):
        """The total elapsed time of the run, in number of milliseconds since the UNIX epoch."""
        return self._duration

    @property
    def artifact_location(self):
        """The artifact location for the current run."""
        return self._artifact_location

    @property
    def run_status(self):
        """
        One of the values in /entities/lc_run_status.py
        describing the status of the run.
        """
        return self._run_status

    @property
    def note(self):
        """
        The extra information for the current run.
        This value is set by user.
        """
        return self._note

    @property
    def path(self):
        """
        the name of current selected notebook.
        """
        return self._path

    @property
    def model_path(self):
        """
        the path of model file.
        """
        return self._model_path

    @property
    def json_path(self):
        """
        the path of model json file.
        """
        return self._json_path

    def to_proto(self):
        proto = ProtoLcRunInfo()
        proto.name = self.run_name
        proto.userId = self.user_id
        proto.creaDt = self.start_time
        proto.endDt = self.end_time
        proto.duration = self.duration
        proto.afLoc = self.artifact_location
        proto.status = RunStatus.from_string(self.run_status)
        proto.note = self.note
        proto.path = self._path
        proto.modelPath = self._model_path
        proto.jsonPath = self._json_path
        return proto

    @classmethod
    def from_proto(cls, proto):
        end_time = proto.endDt
        # The proto2 default scalar value of zero indicates that the run's end time is absent.
        # An absent end time is represented with a NoneType in the `RunInfo` class
        if end_time == 0:
            end_time = None
        return cls(user_id=proto.userId,
                   start_time=proto.creaDt,
                   end_time=proto.endDt,
                   duration=proto.duration,
                   artifact_location=proto.afLoc,
                   run_status=proto.status,
                   model_path=proto.modelPath,
                   json_path=proto.jsonPath,
                   run_name=proto.name,
                   note=proto.note)
