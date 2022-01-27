class StateStorage:
    def __init__(self):
        self.state = False

    def set_ready_state(self, ready_state: bool) -> None:
        self.state = ready_state

    def get_ready_state(self) -> bool:
        return self.state
