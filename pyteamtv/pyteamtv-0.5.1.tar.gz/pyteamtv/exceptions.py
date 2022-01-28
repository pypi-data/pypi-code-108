class PyTeamTVError(Exception):
    pass


class TeamNotFound(PyTeamTVError):
    pass


class InputError(PyTeamTVError):
    pass
