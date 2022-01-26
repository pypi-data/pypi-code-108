from cognite.air._spaces_api import SpacesAPI
from cognite.client import CogniteClient


class AIRAdmin:
    """AIRAdmin client to create, edit, and delete spaces and groups.

    Args:
        client (CogniteClient): Cognite client
        staging (bool): If groups and spaces should be added to staging or production (True is default)
    """

    def __init__(self, client: CogniteClient, staging: bool = True):
        self.client = client
        self.staging = staging
        self.spaces = SpacesAPI(self.client, self.staging)
