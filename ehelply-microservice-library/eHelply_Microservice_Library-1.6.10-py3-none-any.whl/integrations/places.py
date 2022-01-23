from ehelply_bootstrapper.integrations.integration import Integration
from ehelply_bootstrapper.utils.state import State
from ehelply_microservice_library.integrations.fact import get_fact_endpoint


class Places(Integration):
    def __init__(self) -> None:
        """
        Setup the microservice
        """
        super().__init__("places")

        # M2M contains a configured python requests instance which you should use for API requests.
        #  ie. self.m2m.requests
        self.m2m = State.integrations.get("m2m")

    def init(self):
        """
        STEP 0: Initialize the integration.
        :return:
        """
        super().init()

    def load(self):
        """
        STEP 1: Load the integration
        :return:
        """
        super().load()

    @staticmethod
    def get_base_url() -> str:
        """
        Get the base URL of this microservice
        :return:
        """
        return get_fact_endpoint('ehelply-places')
