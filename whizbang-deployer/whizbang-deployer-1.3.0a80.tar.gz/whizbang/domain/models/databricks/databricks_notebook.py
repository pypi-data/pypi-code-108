class DatabricksNotebook:
    def __init__(self, source_path: str, target_path: str = None, language: str = None):
        self.language = language or 'PYTHON'
        self.target_path = target_path or '/'
        self.source_path = source_path
