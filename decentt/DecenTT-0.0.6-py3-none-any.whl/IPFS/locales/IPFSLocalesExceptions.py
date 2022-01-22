class BootstrapNodeError(Exception):
    """
        Subjected: Bootstrap Node reading failure
    """
    def __init__(self, error:Exception = Exception("Unidentified Internal Bootstrap Error")):
        self.error = error

    def __str__(self):
        return f"Bootstrap Identification Failure : {self.error}"

class InvalidBootstrap(Exception):
    """
        Subjected: Bootstrap node specified is invalid
    """