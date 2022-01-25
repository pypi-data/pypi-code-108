class Notifier:
    def __init__(self, _id) -> None:
        self.id = _id

    def send(self, title: str, description: str, diff: str):
        raise NotImplementedError()
