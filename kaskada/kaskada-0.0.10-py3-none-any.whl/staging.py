"""
Copyright (C) 2021 Kaskada Inc. All rights reserved.

This package cannot be used, copied or distributed without the express
written permission of Kaskada Inc.

For licensing inquiries, please contact us at info@kaskada.com.
"""

from kaskada.client import Client
import kaskada
import kaskada.api.v1alpha.staged_file_pb2 as staged_pb

import datetime
import grpc
import hashlib
import io
import os
import random
import requests
import pandas as pd
import tempfile

def list_staged_files(search: str = None, client: Client = None) -> staged_pb.ListStagedFilesResponse:
    """
    Lists staged files

    Args:
        search (str, optional): Name to search staged files. Defaults to None.
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        staged_pb.ListStagedFilesResponse: List of Staged Files
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    try:
        kaskada.validate_client(client)
        req = staged_pb.ListStagedFilesRequest(
            search = search
        )
        return client.stagingStub.ListStagedFiles(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def get_staged_file(staged_file, client: Client = None) -> staged_pb.GetStagedFileResponse:
    """
    Gets a staged file given a file ID.

    Args:
        file (Union[staged_pb.CreateStagedFileResponse, staged_pb.StagedFile,  str]): Staged file object
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        staged_pb.GetStagedFileResponse: Staged File
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    file_id = None
    if isinstance(staged_file, staged_pb.CreateStagedFileResponse):
        file_id = staged_file.file.file_id
    elif isinstance(staged_file, staged_pb.StagedFile):
        file_id = staged_file.file_id
    elif isinstance(staged_file, str):
        file_id = staged_file
    else:
        raise Exception('invalid parameters passed. please provide the staged file ID or create staged file response')

    try:
        kaskada.validate_client(client)
        req = staged_pb.GetStagedFileRequest(
            file_id = file_id
        )
        return client.stagingStub.GetStagedFile(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def upload_staged_data(staged_file: staged_pb.CreateStagedFileResponse, f: io.BufferedReader, client: Client = None):
    """
    Uploads a generic buffered reader to a staged file

    Args:
        staged_file (staged_pb.CreateStagedFileResponse): The result of the create_staged_file call.
        f (io.BufferedReader): The buffered reader to stage.
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        None (if successful)
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    headers = { 'X-Amz-Meta-Filename' : staged_file.file.file_name }
    http_response = requests.put(staged_file.url, headers=headers, data = f)
    if http_response.status_code != 200:
        raise Exception('Unable to upload file. Resulted in status code: {} and message: {}'.format(http_response.status_code, http_response.content))


def create_staged_file_api(file_name: str, content_id: str, client: Client = None) -> staged_pb.CreateStagedFileResponse:
    """
    Creates a staged file given the file name and content id (hash)

    Args:
        file_name (str): The name of the file (used for metadata)
        content_id (str, optional): The content id of the file. Defaults to None.
        client (Client, optional): The Kaskada Client. Defaults to kaskada.KASKADA_DEFAULT_CLIENT.

    Returns:
        staged_pb.CreateStagedFileResponse: Staged File
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT
    try:
        kaskada.validate_client(client)
        req = staged_pb.CreateStagedFileRequest(
            file = staged_pb.StagedFile(
                file_name = file_name,
                content_id = content_id
            )
        )
        return client.stagingStub.CreateStagedFile(req, metadata=client.get_metadata())
    except grpc.RpcError as e:
        kaskada.handleGrpcError(e)
    except Exception as e:
        kaskada.handleException(e)

def create_staged_file(source, client: Client = None) -> staged_pb.CreateStagedFileResponse:
    """
    Entry point to create a staged file

    Args:
        source ([str, pandas.Dataframe]): The source to create the staged file from
        client (Kaskada.Client, optional): The Kaskada Client. Defaults to global client.

    Raises:
        Exception: Invalid parameters (only path or dataframe) is accepted

    Returns:
        staged_pb.CreateStagedFileResponse: Staged File
    """
    if client == None:
        client = kaskada.KASKADA_DEFAULT_CLIENT

    if isinstance(source, str):
        f = open(source,'rb')
        file_name = os.path.basename(f.name)
        # Generate the content ID which is the MD5 hash of the file
        content_id = hashlib.md5(f.read()).hexdigest()
        staged_file = create_staged_file_api(file_name, content_id, client = client)
        f.close()
        f = open(source, 'rb')
        upload_staged_data(staged_file, f, client = client)
        return staged_file
    elif isinstance(source, pd.DataFrame):
        # Content ID is the Data Frame MD5 hash which is computed off the values
        content_id = hashlib.md5(pd.util.hash_pandas_object(source).values).hexdigest()
        # Generate a name for the dataframe as the current time + random number.parquet
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        base_name = "{}_{}.parquet".format(current_time, random.randint(0, 1000))
        staged_file = create_staged_file_api(base_name, content_id, client = client)
        with tempfile.TemporaryDirectory() as tmpdirname:
            file_name = os.path.join(tmpdirname, staged_file.file.file_name)
            # write to tempfile in `tmpdirname`
            source.to_parquet(path = file_name, engine='pyarrow', allow_truncated_timestamps=True, use_deprecated_int96_timestamps=True)
            # upload tempfile from `tmpdirname`
            upload_staged_data(staged_file, open(file_name, "rb"))
            return staged_file
    else:
        raise Exception('invalid parameters passed. please provide the path or dataframe as the first parameter')