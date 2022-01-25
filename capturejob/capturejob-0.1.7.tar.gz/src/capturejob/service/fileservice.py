import io
import json
import os
import pdb
from collections import namedtuple

from azure.storage.blob import (BlobClient, BlobServiceClient, ContainerClient,
                                __version__)
from dyndebug import Debug
from loguru import logger


def FileService(config):

    fileService = namedtuple(
        "FileService", "upload"
    )

    debug = Debug("fileservice")
    
    def upload(fullpath:str, folder:str,filename:str):

        debug(config)
        remotepath = f"{folder}/{filename}"
        debug(f"Pushing {fullpath} to storage {config.containerName}:{remotepath}")
        # Create a blob client using the local file name as the name for the blob
        
        blob_service_client = BlobServiceClient.from_connection_string(
            config.connectionString
        )
        blob_client = blob_service_client.get_blob_client(
            container=config.containerName, blob=remotepath
        )

        debug("\nUploading to Azure Storage as blob:\n\t" + filename)

        # Upload the created file    
        
        with open(fullpath, "rb") as data:
            blob_client.upload_blob(data, overwrite=True)            

    
    return fileService(upload)
