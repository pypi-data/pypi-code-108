class AggregateEvent:
    def __init__(self, events):
        self.events = [event for event in events if event is not None]

    def set(self):
        for event in self.events:
            event.set()
