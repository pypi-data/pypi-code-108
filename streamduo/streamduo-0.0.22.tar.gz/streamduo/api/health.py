class HealthController:
    """
    Manages interactions with the /health endpoints
    """
    def __init__(self, client):
        self.client = client

    def check_health(self):
        """
        GET request ot the /health endpoint
        :return: Requests Response Object
        """
        return self.client.call_api('GET', "/health")
