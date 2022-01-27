import warnings
class VisibleDeprecationWarning(UserWarning):
    """A DeprecationWarning that users should see."""
    pass

warnings.warn("""appdynamics_bindeps.zmq.eventloop.minitornado is deprecated in pyzmq 14.0 and will be removed.
    Install tornado itself to use zmq with the tornado IOLoop.
    """,
    VisibleDeprecationWarning,
    stacklevel=4,
)
