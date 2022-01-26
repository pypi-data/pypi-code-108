"""
State machine processing.

"""
from microcosm_daemon.reloader import Reloader


class StateMachine:
    """
    A state machine for driving daemon processing.

    """
    def __init__(self, graph, initial_state, never_reload=False):
        self.graph = graph
        self.current_state = initial_state
        self.reloader = Reloader() if graph.metadata.debug and not never_reload else None

    def step(self):
        """
        Take one step through the state transition.

        """
        next_state = None
        with self.graph.error_policy:
            with self.graph.sleep_policy:
                next_state = self.current_state(self.graph)

        if callable(next_state):
            # advance to a new state
            return next_state
        else:
            # stay in the same state
            return self.current_state

    def advance(self):
        """
        Advance once step.

        """
        self.current_state = self.step()
        return self.current_state

    def should_run(self):
        """
        Should the state machine keep running?

        """
        return (
            self.current_state and
            not self.graph.signal_handler.interrupted
        )

    def run(self):
        """
        Run the state machine.

        """
        try:
            with self.graph.signal_handler:
                while self.should_run():
                    self.advance()
                    if self.reloader:
                        self.reloader()
        except Exception:
            pass
