import uuid


class Snapshot:
    def __init__(self, resource_id: str, timestamp: float, content: str) -> None:
        self.resource_id = resource_id
        self.timestamp = timestamp
        self.content = content
        self.id = uuid.uuid4().hex
