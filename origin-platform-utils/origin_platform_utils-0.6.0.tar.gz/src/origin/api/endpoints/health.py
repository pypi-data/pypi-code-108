from ..endpoint import Endpoint


class HealthCheck(Endpoint):
    """
    Health check endpoint. Always returns status 200.
    """
    def handle_request(self):
        pass
