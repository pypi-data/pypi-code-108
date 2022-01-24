class TuttiServerError(Exception):
    def __init__(self, data):
        self.code = data['content']['error_code']
        self.details = data['content']
