"""
    CUSTOM READERS CLASSES
        - Class which manages reader tasks like auth, requests, pagination
"""
import json

from azure.storage.blob import ContainerClient
from azure.core.exceptions import ResourceNotFoundError


class CustomAzureReader():
    """
        Custom Azure Reader
    """

    # pylint: disable=super-init-not-called
    def __init__(self, sas_token_path: str):
        self.container_client = self.get_container_client(sas_token_path)

    @staticmethod
    def get_container_client(
            sas_token_path
    ):
        """
        Create a client to communicate with Sailthru
        Args:
            sas_token_path: The file path to sas token
        Returns:
            A service that is connected to the specified API.
        """
        with open(sas_token_path) as json_file:
            data = json.load(json_file)

        return ContainerClient.from_container_url(data['sas_token'])

    def pull_file(self, file_name):
        """
            Pulls the data file from Azure blob
            :return: storage downloader object
        """
        try:
            byte_sequence = self.container_client.download_blob(file_name).readall()
            return json.loads(byte_sequence.decode("utf-8"))
        except ResourceNotFoundError as exception:
            print(
                'Could not find specified blob: {exception}'.format(
                    exception=str(exception)
                )
            )

            return None

