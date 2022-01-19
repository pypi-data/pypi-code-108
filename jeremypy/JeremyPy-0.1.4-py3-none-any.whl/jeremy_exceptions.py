class CSVFileNotFoundError(Exception):
    def __init__(self, path, message="CSV file does not exist"):
        self.path = path
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.path} -> {self.message}'


class JSONFileNotFoundError(Exception):
    def __init__(self, path, message="JSON file does not exist"):
        self.path = path
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.path} -> {self.message}'


class InvalidStyleError(Exception):
    def __init__(self, style, message="Invalid style"):
        self.style = style
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.style}'
