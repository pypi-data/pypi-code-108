class LockFailed(Exception):
    """ Exception to indicate a :py:class:`~momotor.shared.state.StateABC` subclass could not acquire the lock """
    pass
