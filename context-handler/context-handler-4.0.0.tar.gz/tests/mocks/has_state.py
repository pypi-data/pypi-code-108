from .state import State


class MockApp:
    state: State
    context: State
    ctx: State

    def __init__(self, state_attr: str) -> None:
        setattr(self, state_attr, State())


class HasState:
    def __init__(self) -> None:
        self.state = State()
        self.app = MockApp("state")


class HasContext:
    def __init__(self) -> None:
        self.context = State()
        self.app = MockApp("context")


class HasCtx:
    def __init__(self) -> None:
        self.ctx = State()
        self.app = MockApp("ctx")
