class TaskFailed(Exception):
    """
    This indicated a failure with an expected or known reason
    """
    pass


class TaskTimeout(Exception):
    """
    The Task does not finish on time
    """
    pass


class TaskKilledByQuitSignal(Exception):
    """
    A kill signal received before the Task finishes
    """
    pass


class TaskKilledByMonitoringError(Exception):
    """
    An unexpected error occurred while the Worker is monitoring the Task running
    """
    pass
