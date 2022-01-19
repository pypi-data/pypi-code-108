class MongoDfException(Exception):
    def __init__(self, message=""):
        self.message = f"MongoDf Exception: {message}"
        super().__init__(self.message)
