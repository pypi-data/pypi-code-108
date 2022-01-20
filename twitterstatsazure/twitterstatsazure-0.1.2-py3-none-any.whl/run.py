import json
from twitterstatsazure.secrets import AZURE_CONNECTION_STRING
from twitterstatsazure.stats import t1, t2, get_follower_data


def main():
    # print("Hello World")
    # t1()
    # t2()
    # followers = get_follower_data()

    import os, uuid
    from azure.storage.blob import (
        BlobServiceClient,
        BlobClient,
        ContainerClient,
        __version__,
    )

    try:
        print("Azure Blob Storage v" + __version__ + " - Python quickstart sample")

        # Quick start code goes here

    except Exception as ex:
        print("Exception:")
        print(ex)

    blob_service_client = BlobServiceClient.from_connection_string(
        AZURE_CONNECTION_STRING
    )
    # Create a unique name for the container
    container_name = str("containertest1")

    # Create the container
    # container_client = blob_service_client.create_container(container_name)

    # container_client = blob_service_client.get_container_client(container_name)

    blob_service_client: BlobServiceClient
    blob_client = blob_service_client.get_blob_client(
        container=container_name, blob="test4"
    )

    blob_client.upload_blob(json.dumps(dict(test1="test3")))
