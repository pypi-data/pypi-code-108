class PanicException(Exception):
    def __init__(self, place: str, reason: str, suggestion: str):
        super().__init__("\n".join([place, reason, suggestion]))
        self.place: str = place
        self.reason: str = reason
        self.suggestion: str = suggestion

    def print(self) -> None:
        print('🔥 ' + self.place)
        print(self.reason)
        if self.suggestion:
            print(self.suggestion)
