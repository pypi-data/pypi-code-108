class VecticeError(Exception):
    def __init__(self, method_name: str, root_cause: Exception):
        self.method = method_name
        self.root_cause = root_cause

    def __str__(self):
        return f"Error executing {self.method}: {str(self.root_cause)}"
