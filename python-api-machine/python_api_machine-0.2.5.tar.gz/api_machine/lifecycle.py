from dataclasses import dataclass, field

STATE_WILDCARD = "*"


@dataclass
class Transition:
    state: str
    action: str
    target: str
    metadata: dict = field(default_factory=dict)


class StateMachine:
    def __init__(self, transitions=None):
        self.transitions = transitions or []

    def __getitem__(self, key):
        state, action = key
        for transition in self.transitions:
            if transition.state not in [STATE_WILDCARD, state]:
                continue

            if transition.action != action:
                continue

            return transition

        raise KeyError(f"No transition {action} on {state=}")

    def do(self, current_state, action):
        try:
            return self[current_state, action]
        except IndexError:
            raise ValueError(
                f"Invalid action {action} on state {current_state}"
            )


CrudLifeCycle = [
    Transition(None, 'create', 'active'),
    Transition('active', 'update', 'active'),
    Transition('active', 'delete', 'deleted'),
]
