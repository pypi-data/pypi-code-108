class IndexTrackingIterator:
    def __init__(self, lines):
        self.iterator = iter(lines)
        self.current_index = 0

    def __next__(self):
        item = next(self.iterator)
        self.current_index += 1
        return item
