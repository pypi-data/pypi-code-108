class DatabricksToken:
    def __init__(self, token_value: str = None, token_lifespan_seconds: int = None, comment: str = None):
        self.token_value = token_value
        self.token_lifespan_seconds = token_lifespan_seconds
        self.comment = comment
