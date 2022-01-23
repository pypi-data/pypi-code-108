from dataclasses import dataclass


@dataclass
class MockClient:
    is_closed: bool

    def close(self):
        self.is_closed = True
